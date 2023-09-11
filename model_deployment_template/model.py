import numpy as np
import pandas as pd
import sklearn as sk

from pydantic import BaseModel
from typing import Optional, Iterable, Any, Dict

# import joblib
import pickle

'crim', 'zn', 'indus', 'chas', 'nox', 'rm', 'age', 'dis', 'rad', 'tax', 'ptratio', 'lstat'



# Define Raw Input Schema
class InputSchema(BaseModel):
    crim: float 
    zn: int 
    indus: float
    chas: int
    nox: float
    rm: float
    age: float
    dis: float
    rad: int
    tax: int
    ptratio: float
    lstat: float

    # @classmethod
    # def parse_iterable(cls, values: Iterable):
    #     return cls.parse_obj(dict(zip(cls.__fields__, values)))

class Preprocessor:

    def __init__(self):
        # Load preprocessor tools 
        # self.scaler = joblib.load("model/scaler.pkl")
        with open("model/scaler.pkl", "rb") as file:
            self.scaler = pickle.load(file)
    
    def preprocess(self, raw_data):
        # Steps for preprocessing raw_data
        # array = np.array(raw_data)
        # array = array.reshape((1, -1))

        raw_data_dict = raw_data.dict()
        df = pd.DataFrame([raw_data_dict], columns=list(raw_data_dict.keys()))

        data = self.scaler.transform(df)

        data_with_column_name = pd.DataFrame(data, columns=df.columns)

        return data_with_column_name

    def batch_preprocess(self, items):
        # Steps for preprocessing raw_data
        # array = np.array(raw_data)
        # array = array.reshape((1, -1))

        list_raw_data_dict = [raw_data.dict() for raw_data in items]
        df = pd.DataFrame(list_raw_data_dict, columns=list(list_raw_data_dict[0].keys()))

        data = self.scaler.transform(df)

        data_with_column_name = pd.DataFrame(data, columns=df.columns)

        return data_with_column_name

class Model:

    def __init__(self):
        # Load model
        # self.model = joblib.load("model/rf_model.pkl")
        with open("model/rf_model.pkl", "rb") as file:
            try:
                self.model = pickle.load(file)
            except Exception as e:
                print(e)
                position = file.tell()
                file.seek(position)
                self.model = pickle.load(file)
                # foo.__getinitargs__ = a

            # print str(obj)
            
            # self.model = pickle.load(file)
    
    def model_predict(self, data):
        # Define how model makes prediction with processed input data
        pred = self.model.predict(data)
        return pred[0]
    
    def model_batch_predict(self, batch_data):
        # Define how model makes prediction with processed input data
        batch_pred = self.model.predict(batch_data)
        return batch_pred


if __name__ == "__main__":
    my_preprocessor = Preprocessor()
    my_model = Model()

    ########## INPUT TEST DATA #########
    test_input = {
        "crim": 0.03237,
        "zn": 0,
        "indus": 2.18,
        "chas": 0,
        "nox": 0.458,
        "rm": 6.998,
        "age": 45.8,
        "dis": 6.0622,
        "rad": 3,
        "tax": 222,
        "ptratio": 18.7,
        "lstat": 2.94
    }
    
    raw_data = InputSchema(**test_input)

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




