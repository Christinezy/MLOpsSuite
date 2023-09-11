# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Translate sentences from the input stream.
# The model will be faster is sentences are sorted by length.
# Input sentences must have the same tokenization and BPE codes than the ones used in the model.
#
# Usage:
#     python translate.py
#     --src_lang cpp --tgt_lang java \
#     --model_path trained_model.pth < input_code.cpp
#

import argparse
import os
import sys
import fileinput

import fastBPE
import torch

import preprocessing.src.code_tokenizer as code_tokenizer
from XLM.src.data.dictionary import Dictionary, BOS_WORD, EOS_WORD, PAD_WORD, UNK_WORD, MASK_WORD
from XLM.src.model import build_model
from XLM.src.utils import AttrDict

SUPPORTED_LANGUAGES = ['cpp', 'java', 'python']


def get_parser():
    """
    Generate a parameters parser.
    """
    # parse parameters
    parser = argparse.ArgumentParser(description="Translate sentences")

    # model
    parser.add_argument("--model_path", type=str,
                        default="", help="Model path")
    parser.add_argument("--src_lang", type=str, default="",
                        help=f"Source language, should be either {', '.join(SUPPORTED_LANGUAGES[:-1])} or {SUPPORTED_LANGUAGES[-1]}")
    parser.add_argument("--tgt_lang", type=str, default="",
                        help=f"Target language, should be either {', '.join(SUPPORTED_LANGUAGES[:-1])} or {SUPPORTED_LANGUAGES[-1]}")
    parser.add_argument("--BPE_path", type=str,
                        default="data/BPE_with_comments_codes", help="Path to BPE codes.")
    parser.add_argument("--beam_size", type=int, default=1,
                        help="Beam size. The beams will be printed in order of decreasing likelihood.")

    return parser





class Translator:
    def __init__(self, params):
        reloaded = torch.load(params.model_path, map_location='cpu')
        reloaded['encoder'] = {(k[len('module.'):] if k.startswith('module.') else k): v for k, v in
                               reloaded['encoder'].items()}
        assert 'decoder' in reloaded or (
            'decoder_0' in reloaded and 'decoder_1' in reloaded)
        if 'decoder' in reloaded:
            decoders_names = ['decoder']
        else:
            decoders_names = ['decoder_0', 'decoder_1']
        for decoder_name in decoders_names:
            reloaded[decoder_name] = {(k[len('module.'):] if k.startswith('module.') else k): v for k, v in
                                      reloaded[decoder_name].items()}

        self.reloaded_params = AttrDict(reloaded['params'])

        # build dictionary / update parameters
        self.dico = Dictionary(
            reloaded['dico_id2word'], reloaded['dico_word2id'], reloaded['dico_counts'])
        assert self.reloaded_params.n_words == len(self.dico)
        assert self.reloaded_params.bos_index == self.dico.index(BOS_WORD)
        assert self.reloaded_params.eos_index == self.dico.index(EOS_WORD)
        assert self.reloaded_params.pad_index == self.dico.index(PAD_WORD)
        assert self.reloaded_params.unk_index == self.dico.index(UNK_WORD)
        assert self.reloaded_params.mask_index == self.dico.index(MASK_WORD)

        # build model / reload weights
        self.reloaded_params['reload_model'] = ','.join([params.model_path] * 2)
        encoder, decoder = build_model(self.reloaded_params, self.dico)

        self.encoder = encoder[0]
        self.encoder.load_state_dict(reloaded['encoder'])
        assert len(reloaded['encoder'].keys()) == len(
            list(p for p, _ in self.encoder.state_dict().items()))

        self.decoder = decoder[0]
        self.decoder.load_state_dict(reloaded['decoder'])
        assert len(reloaded['decoder'].keys()) == len(
            list(p for p, _ in self.decoder.state_dict().items()))

        self.encoder.cpu()
        self.decoder.cpu()

        self.encoder.eval()
        self.decoder.eval()
        self.bpe_model = fastBPE.fastBPE(os.path.abspath(params.BPE_path))

    def translate(self, input, lang1, lang2, n=1, beam_size=1, sample_temperature=None, device='cuda:0'):
        with torch.no_grad():
            assert lang1 in {'python', 'java', 'cpp'}, lang1
            assert lang2 in {'python', 'java', 'cpp'}, lang2

            DEVICE = device
            tokenizer = getattr(code_tokenizer, f'tokenize_{lang1}')
            detokenizer = getattr(code_tokenizer, f'detokenize_{lang2}')
            lang1 += '_sa'
            lang2 += '_sa'

            lang1_id = self.reloaded_params.lang2id[lang1]
            lang2_id = self.reloaded_params.lang2id[lang2]

            tokens = [t for t in tokenizer(input)]
            tokens = self.bpe_model.apply(tokens)
            tokens = ['</s>'] + tokens + ['</s>']
            input = " ".join(tokens)
            # create batch
            len1 = len(input.split())
            len1 = torch.LongTensor(1).fill_(len1).to(DEVICE)

            x1 = torch.LongTensor([self.dico.index(w)
                                   for w in input.split()]).to(DEVICE)[:, None]
            langs1 = x1.clone().fill_(lang1_id)

            enc1 = self.encoder('fwd', x=x1, lengths=len1,
                                langs=langs1, causal=False)
            enc1 = enc1.transpose(0, 1)
            if n > 1:
                enc1 = enc1.repeat(n, 1, 1)
                len1 = len1.expand(n)

            if beam_size == 1:
                x2, len2 = self.decoder.generate(enc1, len1, lang2_id,
                                                 max_len=int(
                                                     min(self.reloaded_params.max_len, 3 * len1.max().item() + 10)),
                                                 sample_temperature=sample_temperature)
            else:
                x2, len2 = self.decoder.generate_beam(enc1, len1, lang2_id,
                                                      max_len=int(
                                                          min(self.reloaded_params.max_len, 3 * len1.max().item() + 10)),
                                                      early_stopping=False, length_penalty=1.0, beam_size=beam_size)
            tok = []
            for i in range(x2.shape[1]):
                wid = [self.dico[x2[j, i].item()] for j in range(len(x2))][1:]
                wid = wid[:wid.index(EOS_WORD)] if EOS_WORD in wid else wid
                tok.append(" ".join(wid).replace("@@ ", ""))

            results = []
            for t in tok:
                results.append(detokenizer(t))
            return results

def trans(source_lang, target_lang, filename, output_path):
    
    parser = get_parser()
    #params = parser.parse_args() 
    #params = params.split(',')
    model = ''
    if (source_lang == 'java') or (source_lang == 'cpp' and target_lang == 'java'):
      model = './models/model_1.pth'
    elif (source_lang == 'python') or (source_lang == 'cpp' and target_lang == 'python'):
      model = './models/model_2.pth'
    print(model)
    #parser = get_parser()
    lparser = parser.parse_args(['--model_path', model,'--src_lang', source_lang, '--tgt_lang', target_lang, '--BPE_path', './data/BPE_with_comments_codes'])

    translator = Translator(lparser)

    filen = open(filename, 'r')

    input = filen.read().strip()

    # input = sys.stdin.read().strip()

    with torch.no_grad():
        output = translator.translate(
            input, lang1=lparser.src_lang, lang2=lparser.tgt_lang, beam_size=lparser.beam_size, device='cpu')
    filen.close()

    filetype = ''
    if target_lang == 'python':
        filetype = '.py'
    elif target_lang == 'cpp':
        filetype = '.cpp'
    elif target_lang =='java':
        filetype = '.java'

    sys.stdout = open(f'{output_path}'+filetype, 'w')
    for out in output:
        #print("=" * 20)
        print(out)

    sys.stdout.close()

if __name__ == "__main__":
    trans('java','cpp','./test_files/java_code.java', "./output/java_cpp")

