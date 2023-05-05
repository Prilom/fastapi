import os
from google.cloud import storage


class GCStorage:

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\prilo\\OneDrive\\Desktop\\KeepCoding\\Proyecto_final\\repositorio\\BullyingProject\\API\\brainwave-382317-f5cea375d087.json'
        self.storage_client = storage.Client()
        self.bucket_name = 'depliegue-modelo'

    def download_blob(self, source_blob_name, destination_file_name):
        """descarga de ficheros del bucket."""
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)

        blob.download_to_filename(destination_file_name)

