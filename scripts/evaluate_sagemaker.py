"""
evaluate_sagemaker.py

This script evaluates a trained machine learning model stored in AWS S3, specifically a model 
trained and exported using Amazon SageMaker. The script performs the following steps:

1. **Download the Model**: Retrieves the model archive (`model.tar.gz`) from an S3 bucket if it's not already present.
2. **Extract the Model**: Unpacks the `model.tar.gz` archive to retrieve the trained model file (`model.pkl`).
3. **Load the Model**: Uses `joblib` to load the extracted machine learning model.
4. **Load Test Data**: Reads preprocessed test datasets (`X_test.csv`, `y_test.csv`) from the `model_data` directory.
5. **Make Predictions**: Uses the trained model to generate predictions on the test data.
6. **Evaluate Model Performance**: Computes key evaluation metrics, including accuracy, precision, recall, F1-score, and AUC.
7. **Display Results**: Prints evaluation metrics to the console.

This script ensures that the model and test datasets exist before proceeding, and it logs each step to aid in debugging. 

Usage:
- Run the script after training and exporting a model in SageMaker.
- Ensure the `.env` file contains correct AWS credentials and S3 bucket information.
- Ensure the `config.py` file correctly defines the paths for models and test data."
"""

import joblib
import boto3
import pandas as pd
import numpy as np
import tarfile
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import MODEL_FILES, MODEL_STORAGE, MODEL_DIR

# Load environment variables
load_dotenv()

# AWS & SageMaker Configuration
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
MODEL_KEY = os.getenv("MODEL_KEY")

# Ensure models directory exists 
os.makedirs(MODEL_DIR, exist_ok=True)
print(f"Models directory ready: {MODEL_DIR}")

model_tar_path = MODEL_STORAGE["model_tar"]
model_pkl_path = MODEL_STORAGE["model_pkl"]

# Debug: Print environment variables
print(f"AWS_REGION: {AWS_REGION}")
print(f"S3_BUCKET: {S3_BUCKET}")

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Download Model from S3
if not model_tar_path.exists():
    print(f"⬇Downloading model from s3://{S3_BUCKET}/{MODEL_KEY}...")
    s3_client.download_file(S3_BUCKET, MODEL_KEY, str(model_tar_path))
    print(f"Model downloaded successfully to {model_tar_path}.")
else:
    print(f"Model file already exists at {model_tar_path}. Skipping download.")

# Extract Model
print("Extracting model archive...")
with tarfile.open(model_tar_path, "r:gz") as tar:
    tar.extractall(MODEL_DIR)  # Extract into `models/`

# Verify Extraction
if not model_pkl_path.exists():
    raise FileNotFoundError(f"No valid model file found at {model_pkl_path}. Check extraction!")
print(f"Model successfully extracted: {model_pkl_path}")

# Load Model
print("Loading trained model...")
model = joblib.load(model_pkl_path)
print("Model loaded successfully!")

# Test set paths
X_test_path = MODEL_FILES["X_test"]
y_test_path = MODEL_FILES["y_test"]

print(f"Checking dataset paths: X_test: {X_test_path}, y_test: {y_test_path}")

if not X_test_path.exists() or not y_test_path.exists():
    raise FileNotFoundError("Test dataset files not found!")

print("Loading test dataset...")
X_test = pd.read_csv(X_test_path, header=None)
y_test = pd.read_csv(y_test_path, header=None).squeeze()

# Ensure feature alignment
expected_features = getattr(model, "feature_names_in_", None)
if expected_features:
    X_test.columns = expected_features
else:
    print("Warning: Model does not have feature names stored. Using default column indices.")

# Make Predictions
print("Making predictions...")
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # Probability of class 1

# Compute Evaluation Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

# Print Evaluation Results
print("\nModel Evaluation Results:")
print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 Score: {f1:.3f}")
print(f"AUC: {auc:.3f}")