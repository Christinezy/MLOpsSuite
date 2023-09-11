import logging
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import List
from model import Preprocessor, Model, InputSchema

from starlette.responses import RedirectResponse

import numpy as np
import pandas as pd
import sklearn as sk
# import joblib
import pickle

import os


app = FastAPI(
    redoc_url="/",
    docs_url="/",
    root_path=os.environ.get('ROOT_PATH')
    # openapi_prefix="/project1",
    # openapi_url="/project1/openapi.json"
    # root_path = os.environ.get("ROOT_PATH"),
    # openapi_url = "/project1/openapi.json",
    )

# @app.on_event("startup")
# def load_model_and_preprocessor():
my_preprocessor = Preprocessor()

my_model = Model()

# with open("model/rf_model.pkl", "rb") as file:
#     model = pickle.load(file)





# @app.get("/", include_in_schema=False)
# async def root():
#     # return {
#     #     "message": "Hello"
#     # }
#     return RedirectResponse(url="/redoc")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    # print(app.openapi_url, flush=True)
    # openapi_url = app.openapi_url
    # return get_swagger_ui_html(
    #     openapi_url=openapi_url,
    #     title="API",
    # )    
    full_url = "http://localhost" + openapi_url
    # return {
    #     "print": full_url
    # }
    return get_swagger_ui_html(
        openapi_url=full_url,
        title="API",
    )

@app.get("/docs2", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    # root_path = app.root_path
    openapi_url = root_path + app.openapi_url
    # print(app.openapi_url, flush=True)
    # openapi_url = app.openapi_url
    # return get_swagger_ui_html(
    #     openapi_url=openapi_url,
    #     title="API",
    # )    
    full_url = "http://localhost" + openapi_url
    return {
        "print": full_url
    }
    # return get_swagger_ui_html(
    #     openapi_url=full_url,
    #     title="API",
    # )

@app.get("/docs3", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    # print(app.openapi_url, flush=True)
    # openapi_url = app.openapi_url
    # return get_swagger_ui_html(
    #     openapi_url=openapi_url,
    #     title="API",
    # )    
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    # root_path = app.root_path
    openapi_url = root_path + app.openapi_url
    # openapi_url = app.openapi_url
    # return get_swagger_ui_html(
    #     openapi_url=openapi_url,
    #     title="API",
    # )    
    full_url = "http://localhost" + openapi_url
    # return {
    #     "print": full_url
    # }
    return get_redoc_html(
        openapi_url=full_url,
        title="API",
    )

@app.post("/predict")
async def predict(input_data: InputSchema):
    data = my_preprocessor.preprocess(input_data)
    pred = my_model.model_predict(data)

    return {
        "data": pred
    }

@app.post("/batch-predict")
async def predict(items: List[InputSchema]):
    # for 
    # data = my_preprocessor.preprocess(input_data)
    # pred = my_model.model_predict(data)

    batch_data = my_preprocessor.batch_preprocess(items)
    batch_pred = my_model.model_batch_predict(batch_data)
    list_batch_pred = list(batch_pred)
    # print(batch_pred, flush=True)

    return {
        "data": list_batch_pred
    }

@app.get("/get-root", include_in_schema=False)
def read_main(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

@app.get("/test", include_in_schema=False)
def read_main(request: Request):
    return {"status": "Working"}
