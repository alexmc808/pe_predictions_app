"""
config.py

This script defines the directory structure for the pe_predictions_app project.
It centralizes file paths to avoid hardcoded paths in other scripts, ensuring 
scalability and maintainability.

Usage:
- Import this module in other scripts to access file paths dynamically.
- Example: from config import MODEL_FILES
"""

import os
from pathlib import Path

# Get the root directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Define directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ENGINEERED_DATA_DIR = DATA_DIR / "engineered"
MODEL_DATA_DIR = DATA_DIR / "model_data"
MODEL_DIR = BASE_DIR / "models"

# File paths for raw data
RAW_FILES = {
    "comorbidities": RAW_DATA_DIR / "comorbidities.csv",
    "diagnosis": RAW_DATA_DIR / "diagnosis.csv",
    "labs": RAW_DATA_DIR / "labs.csv",
    "treatments": RAW_DATA_DIR / "treatments.csv",
}

# File paths for processed data
PROCESSED_FILES = {
    "preprocessed": PROCESSED_DATA_DIR / "preprocessed.csv",
}

# File paths for engineered data
ENGINEERED_FILES = {
    "engineered": ENGINEERED_DATA_DIR / "engineered.csv",
}

# File paths for model preparation outputs
MODEL_FILES = {
    "X_train": MODEL_DATA_DIR / "X_train.csv",
    "y_train": MODEL_DATA_DIR / "y_train.csv",
    "X_val": MODEL_DATA_DIR / "X_val.csv",
    "y_val": MODEL_DATA_DIR / "y_val.csv",
    "X_test": MODEL_DATA_DIR / "X_test.csv",
    "y_test": MODEL_DATA_DIR / "y_test.csv",
}

# Model Storage Paths
MODEL_STORAGE = {
    "model_tar": MODEL_DIR / "model.tar.gz",
    "model_pkl": MODEL_DIR / "model.pkl",
}