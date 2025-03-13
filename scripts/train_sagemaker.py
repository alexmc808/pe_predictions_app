import boto3
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
import os
from dotenv import load_dotenv

# Load AWS Credentials from .env
load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_TRAINING_DATA = f"s3://{S3_BUCKET}/data/"
S3_MODEL_OUTPUT_PATH = f"s3://{S3_BUCKET}/models/"
SAGEMAKER_ROLE = os.getenv("SAGEMAKER_ROLE")

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()

# Define SageMaker SKLearn Estimator
sklearn_estimator = SKLearn(
    entry_point="train_script.py",
    role=SAGEMAKER_ROLE,
    instance_count=1,
    instance_type="ml.m5.large",
    framework_version="0.23-1",
    sagemaker_session=sagemaker_session,
    input_mode="File",
    output_path=S3_MODEL_OUTPUT_PATH 
)

# Start training job
print(f"Starting training job with data from: {S3_TRAINING_DATA}")
sklearn_estimator.fit({"training": S3_TRAINING_DATA})

# Save trained model path
model_path = sklearn_estimator.model_data
print(f"Model trained and saved at: {model_path}")