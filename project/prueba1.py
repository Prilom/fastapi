import os
import tempfile
from google.cloud import storage
from config import Config

settings = Config()

class GCStorage:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\prilo\\OneDrive\\Desktop\\KeepCoding\\Proyecto_final\\repositorio\\BullyingProject\\API\\brainwave-382317-b97cff57066a.json'
        self.storage_client = storage.Client()
        self.bucket_name = 'depliegue-modelo'
        print('storage_client instance created successfully')

    def download_blob(self, source_blob_name):
        """descarga de ficheros del bucket."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)

        _, temp_local_filename = tempfile.mkstemp()

        blob.download_to_filename(temp_local_filename)

        return temp_local_filename

# Crear una instancia de la clase GCStorage
gc_storage = GCStorage()

model_filename = f'{settings.MODEL_FILE}{settings.MODEL_NAME}.h5'
print(model_filename)

scaler_filename = f'{settings.SCALER_FILE}{settings.SCALER_NAME}.pkl'

# Descargar un archivo del bucket y comprobar si se ha descargado correctamente
try:
    temp_local_filename = gc_storage.download_blob(model_filename)
    print(f'Archivo descargado correctamente: {temp_local_filename}')
except Exception as e:
    print(f'Error al descargar el archivo: {e}')