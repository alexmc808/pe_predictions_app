"""
upload_to_s3.py

This script uploads processed model data files to an S3 bucket.

Key Features:
- Reads AWS credentials & bucket from `.env`
- Uses `config.py` to get `model_data` directory
- Uploads train/val/test datasets to S3

Usage:
    python scripts/upload_to_s3.py
"""

import boto3
import sys
import os
from dotenv import load_dotenv

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import MODEL_DATA_DIR

# Load AWS credentials from .env
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# List of dataset files to upload
dataset_files = ["X_train.csv", "X_val.csv", "X_test.csv", "y_train.csv", "y_val.csv", "y_test.csv"]

def check_bucket():
    """Check if the S3 bucket is accessible."""
    try:
        print(f"Checking if bucket '{S3_BUCKET}' exists...")
        s3_client.head_bucket(Bucket=S3_BUCKET)
        print(f"Bucket '{S3_BUCKET}' is accessible!")
    except Exception as e:
        print(f"S3 Bucket Error: {e}")

def upload_files():
    """Uploads dataset files from MODEL_DATA_DIR to S3."""
    check_bucket()  # Check bucket before upload

    for filename in dataset_files:
        local_path = os.path.join(MODEL_DATA_DIR, filename)
        s3_path = f"model_data/{filename}"  # S3 folder path

        print(f"Checking file: {local_path}")

        if os.path.exists(local_path):
            print(f"Found file: {local_path}")
            try:
                s3_client.upload_file(local_path, S3_BUCKET, s3_path)
                print(f"Uploaded {filename} to s3://{S3_BUCKET}/{s3_path}")
            except Exception as e:
                print(f"Upload failed for {filename}: {e}")
        else:
            print(f"File not found: {local_path}")

if __name__ == "__main__":
    upload_files()