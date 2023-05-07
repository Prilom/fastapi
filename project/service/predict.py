from __future__ import absolute_import

import pickle
import os
#import tensorflow as tf
import datetime

from joblib import load

from project.models.master_model import Master
from project.gcs import GCStorage
from project.config import Config

settings = Config()

class PreprocesingAndPredict:
    """clase que al crear la instancia realiza la descarga de los modelos para """

    def __init__(self):
        self.model_filename = f'{settings.MODEL_FILE}{settings.MODEL_NAME}.h5'
        self.scaler_filename = f'{settings.SCALER_FILE}{settings.SCALER_NAME}.pkl'
        self.bucket_storage = GCStorage(settings.GOOGLE_APPLICATION_CREDENTIALS)

        # Descarga del modelo y scaler del bucket
        self.bucket_storage.download_blob(self.model_filename, 'C:\\Users\\prilo\\OneDrive\\Desktop\\KeepCoding\\Proyecto_final\\repositorio\\BullyingProject\\API\\project\\service\\model.h5')
        self.bucket_storage.download_blob(self.scaler_filename,'C:\\Users\\prilo\\OneDrive\\Desktop\\KeepCoding\\Proyecto_final\\repositorio\\BullyingProject\\API\\project\\service\\skaler.plk')

        # Carga del modelo y scaler desde ficheros locales
        with open('C:\\Users\\prilo\\OneDrive\\Desktop\\KeepCoding\\Proyecto_final\\repositorio\\BullyingProject\\API\\project\\service\\model.h5', 'rb') as f:
            self.model = pickle.load(f)

        with open('C:\\Users\\prilo\\OneDrive\\Desktop\\KeepCoding\\Proyecto_final\\repositorio\\BullyingProject\\API\\project\\service\\skaler.plk', 'rb') as f:
            self.scaler = pickle.load(f)

    def predict(self, data, entry_id):
        # Preprocesamiento de los datos        
        scaled_data = self.scaler.transform(data)

        # Predicción
        predict = self.model.predict(scaled_data)
        self.save_predict_from_db(predict,entry_id )
        return predict
    
    @staticmethod
    def save_predict_from_db(predict, entry_id):
        prediction = ''
        prob_prediction = ''
        registro = Master.get_by_id(entry_id)
        registro.prediction = prediction
        registro.prob_prediction = prob_prediction
        registro.dt_update = datetime.now()
        registro.save()









        

  