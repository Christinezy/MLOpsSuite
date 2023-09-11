import numpy as np
import pandas as pd
import sklearn as sk

from pydantic import BaseModel
from typing import Optional, Iterable, Any, Dict
from sklearn.neural_network import MLPClassifier
# import joblib
import pickle

'crim', 'zn', 'indus', 'chas', 'nox', 'rm', 'age', 'dis', 'rad', 'tax', 'ptratio', 'lstat'



# Define Raw Input Schema
class InputSchema(BaseModel):
    age: int
    job: str 
    marital: str
    education: str
    default: str
    balance: int
    housing: str
    loan: str
    contact: str
    day: int
    month: str
    campaign: int
    pdays: int
    previous: int
    poutcome: str


    # @classmethod
    # def parse_iterable(cls, values: Iterable):
    #     return cls.parse_obj(dict(zip(cls.__fields__, values)))

class Preprocessor:

    def __init__(self):
        # Load preprocessor tools 

        self.num_cols = ['age', 'balance', 'day', 'campaign', 'pdays', 'previous']
        self.cat_cols = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']
        # self.scaler = joblib.load("model/scaler.pkl")
        with open("model/scaler.pkl", "rb") as file:
            self.scaler = pickle.load(file)

        with open("model/encoder.pkl", "rb") as file:
            self.encoder = pickle.load(file)
        
    
    def preprocess(self, raw_data):
        # Steps for preprocessing raw_data
        # array = np.array(raw_data)
        # array = array.reshape((1, -1))

        raw_data_dict = raw_data.dict()
        df = pd.DataFrame([raw_data_dict], columns=list(raw_data_dict.keys()))

        df_ready = df.copy()

        df_ready[self.num_cols] = self.scaler.transform(df[self.num_cols])

        df_encoded = pd.DataFrame(self.encoder.transform(df_ready[self.cat_cols]))
        df_encoded.columns = self.encoder.get_feature_names_out(self.cat_cols)
        
        # Replace Categotical Data with Encoded Data
        df_ready = df_ready.drop(self.cat_cols ,axis=1)
        df_ready = pd.concat([df_encoded, df_ready], axis=1)

        data_with_column_name = df_ready

        return data_with_column_name

    def batch_preprocess(self, items):
        # Steps for preprocessing raw_data
        # array = np.array(raw_data)
        # array = array.reshape((1, -1))

        list_raw_data_dict = [raw_data.dict() for raw_data in items]
        df = pd.DataFrame(list_raw_data_dict, columns=list(list_raw_data_dict[0].keys()))

        df_ready = df.copy()

        df_ready[self.num_cols] = self.scaler.transform(df[self.num_cols])

        df_encoded = pd.DataFrame(self.encoder.transform(df_ready[self.cat_cols]))
        df_encoded.columns = self.encoder.get_feature_names_out(self.cat_cols)
        
        # Replace Categotical Data with Encoded Data
        df_ready = df_ready.drop(self.cat_cols ,axis=1)
        df_ready = pd.concat([df_encoded, df_ready], axis=1)

        data_with_column_name = df_ready

        return data_with_column_name

# with open("model/model2.pkl", "rb") as file:
#     model = pickle.load(file)

class Model:

    def __init__(self):
        # Load model
        # self.model = joblib.load("model/rf_model.pkl")

        # self.model = MLPClassifier(hidden_layer_sizes=(60), max_iter=1000)
        # self.model.load_model("model/rf_model.pkl")
        
        with open("model/model.pkl", "rb") as file:
            model = pickle.load(file)

        self.model = model

        # with open("model/rf_model.pkl", "rb") as file:
        #     try:
        #         self.model = pickle.load(file)
        #     except Exception as e:
        #         print(e)
        #         position = file.tell()
        #         file.seek(position)
        #         self.model = pickle.load(file)
        #         foo.__getinitargs__ = a

        # self.model = pickle.loads(open("./model/rf_model.pkl", 'rb'))

            # print str(obj)
            
            # self.model = pickle.load(file)
    
    def model_predict(self, data):
        # Define how model makes prediction with processed input data
        pred = self.model.predict(data)
        final_pred = list(map(lambda x: 'yes' if x == 1 else 'no', pred))
        return final_pred[0]
    
    def model_batch_predict(self, batch_data):
        # Define how model makes prediction with processed input data
        batch_pred = self.model.predict(batch_data)
        final_batch_pred = list(map(lambda x: 'yes' if x == 1 else 'no', batch_pred))
        return final_batch_pred
    
    def model_predict_proba(self, data):
        # Define how model makes prediction with processed input data
        pred = self.model.predict_proba(data)
        # final_pred = list(map(lambda x: 'yes' if x == 1 else 'no', pred))
        return pred[0]
    
    def model_batch_predict_proba(self, batch_data):
        # Define how model makes prediction with processed input data
        batch_pred = self.model.predict_proba(batch_data)
        # final_batch_pred = list(map(lambda x: 'yes' if x == 1 else 'no', batch_pred))
        return batch_pred


if __name__ == "__main__":
    my_preprocessor = Preprocessor()
    my_model = Model()

    ########## INPUT TEST DATA #########
    test_input = {
        "age": 31,
        "job": "blue-collar",
        "marital": "single",
        "education": "secondary",
        "default": "no",
        "balance": 554,
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "day": 5,
        "month": "feb",
        "campaign": 1,
        "pdays": -1,
        "previous": 0,
        "poutcome": 'unknown'
    }
    
    raw_data = InputSchema(**test_input)

    batch_raw_data = [raw_data, raw_data, raw_data]

    pred = None

    ###################################

    try :
        data = my_preprocessor.preprocess(raw_data)
    except Exception as e:
        print("[ERROR] Preprocessor failed to preprocess raw data")
        print(e)
    else:
        try:
            pred = my_model.model_predict(data)
        except Exception as e:
            print("[ERROR] Model failed to predict")
            print(e)
        else:
            print("Prediction:", pred)
        
        try:
            pred = my_model.model_predict_proba(data)
        except Exception as e:
            print("[ERROR] Model failed to predict proba")
            print(e)
        else:
            print("Prediction proba:", pred)

    
    try :
        batch_data = my_preprocessor.batch_preprocess(batch_raw_data)
    except Exception as e:
        print("[ERROR] Batch Preprocessor failed to preprocess raw data")
        print(e)
    else:
        try:
            preds = my_model.model_batch_predict(batch_data)
        except Exception as e:
            print("[ERROR] Batch Model failed to predict")
            print(e)
        else:
            print("Prediction:", preds)
        
        try:
            preds = my_model.model_batch_predict_proba(batch_data)
        except Exception as e:
            print("[ERROR] Batch Model failed to predict proba")
            print(e)
        else:
            print("Prediction proba:", preds)
    





