import os
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml, load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)

class DataPreprocessor:
    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def preprocess_data(self, df):
        try:
            logger.info("Starting data preprocessing")
            logger.info("Dropping columns")

            df.drop(columns=['Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols = self.config['data_processing']['categorical_features']
            num_cols = self.config['data_processing']['numerical_features']

            logger.info("Applying label encoding")

            label_encoder = LabelEncoder()
            mapping = {}
            for column in cat_cols:
                df[column] = label_encoder.fit_transform(df[column])
                mapping[column] = {label:code for label, code in zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))}
            
            logger.info("Label mappings:")
            for column, mapping in mapping.items():
                logger.info(f"{column}: {mapping}")

            logger.info("Skewness handling")

            skew_threshold = self.config['data_processing']['skewness_threshold']
            skewness = df[num_cols].apply(lambda x: x.skew())

            for column in skewness[skewness > skew_threshold].index:
                df[column] = np.log1p(df[column])
            
            return df
        
        except Exception as e:
            logger.error(f"Error during data preprocessing: {e}")
            raise CustomException("Error during data preprocessing", e)
    
    def handle_imbalance(self, df):
        try:
            logger.info("Handling imbalanced data")
            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            smote = SMOTE(random_state=42)
            X_res, y_res = smote.fit_resample(X, y)

            balanced_df = pd.DataFrame(X_res, columns=X.columns)
            balanced_df['booking_status'] = y_res

            logger.info("Imbalance handling completed")
            return balanced_df
        
        except Exception as e:
            logger.error(f"Error during imbalance handling: {e}")
            raise CustomException("Error during imbalance handling", e)
    
    def feature_selection(self, df):
        try:
            logger.info("Starting feature selection")

            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            model = RandomForestClassifier(random_state=42)
            model.fit(X, y)

            feature_importance = model.feature_importances_
            feature_importance_df = pd.DataFrame({
                'feature': X.columns,
                'importance': feature_importance
            })
            top_feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
            num_features_to_select = self.config['data_processing']['num_features_to_select']

            top_10_features = top_feature_importance_df['feature'].head(num_features_to_select).values

            logger.info(f"Top {num_features_to_select} features selected: {top_10_features.tolist()}")

            top_10_df = df[top_10_features.tolist() + ['booking_status']]

            logger.info("Feature selection completed")
            return top_10_df
        
        except Exception as e:
            logger.error(f"Error during feature selection: {e}")
            raise CustomException("Error during feature selection", e)
        
    def save_data(self, df, file_path):
        try:
            logger.info ("Saving processed data")
            df.to_csv(file_path, index=False)

            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise CustomException("Error saving data", e)
    
    def process(self):
        try:
            logger.info("Loading data from raw directory")
            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            train_df = self.handle_imbalance(train_df)
            test_df = self.handle_imbalance(test_df)

            train_df = self.feature_selection(train_df)
            test_df = test_df[train_df.columns]

            self.save_data(train_df, PROCESSED_TRAIN_FILE_PATH)
            self.save_data(test_df, PROCESSED_TEST_FILE_PATH)

            logger.info("Data preprocessing completed successfully")

        except Exception as e:
            logger.error(f"Error in data preprocessing: {e}")
            raise CustomException("Error in data preprocessing", e)



if __name__ == "__main__":
    preprocessor = DataPreprocessor(
        train_path=TRAIN_FILE_PATH,
        test_path=TEST_FILE_PATH,
        processed_dir=PROCESSES_DIR,
        config_path=CONFIG_PATH
    )
    preprocessor.process()