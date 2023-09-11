import * as React from "react";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { Box } from "@mui/joy";
import { useDispatch } from "react-redux";
import { useState } from "react";
import { codePortingRequestThunk } from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);

export default function CodePortingModal(props) {
  const { file_name, language_type, state, open, handleClose, setAlertOpen } = props; 
  const lang = language_type == "c++" ? "cpp" : language_type;
  const dispatch = useDispatch();

  const [target, setTarget] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    dispatch(
      codePortingRequestThunk({
      pid: projectId,
      vid: state,
      payload: {
        filename: file_name,
        source_lang: data.get("source"),
        target_lang: data.get("target")
      }
      })
    ); 
    setAlertOpen(true);
    handleClose();
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog
        sx={{ maxWidth: 500, width: "80%" }}
      >
        <ModalClose />
        <Typography id="basic-modal-dialog-title" component="h2">
          Code Porting
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <Stack justifyContent="center" spacing={2}>
            <FormControl>
              <FormLabel>Source language</FormLabel>
              <Select
                id="source"
                name="source"
                placeholder= "Source language"
                value={lang}
                sx={{ maxHeight: 40 }}
              >
                <MenuItem value={lang}>{language_type}</MenuItem>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Select target language</FormLabel>
              <Select
                id="target"
                name="target"
                placeholder= "Select target language"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                sx={{ maxHeight: 40 }}
              >
                {
                    (language_type == "java" || language_type == "python") &&
                    <MenuItem value="cpp">C++</MenuItem>
                }
                {
                    (language_type == "python" || language_type == "c++") &&
                    <MenuItem value="java">Java</MenuItem>
                }
                {
                    (language_type == "java" || language_type == "c++") &&
                    <MenuItem value="python">Python</MenuItem>
                }
              </Select>
            </FormControl>
            <Button type="submit">Submit</Button>
          </Stack>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
