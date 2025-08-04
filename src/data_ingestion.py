import os
import pandas as pd
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.custom_exception import CustomException
from src.logger import get_logger
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.bucket_file_name = self.config["bucket_file_name"]
        self.train_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data Ingestion initialized with bucket: {self.bucket_name}, file: {self.bucket_file_name}")
    
    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.bucket_file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logger.info(f"File {self.bucket_file_name} downloaded from GCP bucket {self.bucket_name} to {RAW_FILE_PATH}")
        
        except Exception as e:
            logger.error(f"Error downloading file from GCP: {e}")
            raise CustomException(f"Error downloading file from GCP: {e}")
        
    def split_data(self):
        try:
            logger.info("Starting data split process")
            data = pd.read_csv(RAW_FILE_PATH)
            train_data, test_data = train_test_split(data, test_size=1-self.train_ratio, random_state=42)
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)
            logger.info(f"Data split completed. Train data saved to {TRAIN_FILE_PATH}, Test data saved to {TEST_FILE_PATH}")
        except Exception as e:
            logger.error(f"Error during data split: {e}")
            raise CustomException(f"Error during data split: {e}") 
    
    def run(self):
        try:
            logger.info("Starting data ingestion process")
            self.download_csv_from_gcp()
            self.split_data()
            logger.info("Data ingestion process completed successfully")
        except Exception as e:
            logger.error(f"Error in data ingestion process: {e}")
        finally:
            logger.info("Data ingestion process finished")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()