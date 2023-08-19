#from google_drive_downloader import GoogleDriveDownloader as gdd
import streamlit as st
from fastai.tabular.all import *
import pandas as pd
import pathlib


model_path = pathlib.Path(__file__).parents[1].joinpath("model\main_model.pkl")
#gdd.download_file_from_google_drive(file_id="1X4ruvSrBwm4R83of4J0OLmLLYqXZgQHv",
#                                    dest_path=model_path)

def model_predict(hum, temp, pressure, rain):
    loaded_model = load_learner(model_path)
    to_predict = pd.Series([hum, temp, pressure, rain], index=['humidity', 'temperature', 'pressure', 'rain'])
    return loaded_model.predict(to_predict)
   # return 6.9


if __name__ == "__main__":
    #test = {'season' : seasonList[0], 'mnth' : 5, 'hr': 18, 'workingday' : "True", "weathersit":weatherList[0], 'temp':0.4, 'hum':0.4, 'windspeed' : 0.5, 'id' : 0}
    print(model_predict(50,50,50,50))
    None