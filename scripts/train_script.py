import os
import subprocess

# Install dependencies required inside SageMaker
print("Installing dependencies in SageMaker...")
subprocess.call(
    [
        "pip",
        "install",
        "boto3==1.24.17",
        "botocore==1.27.18",
        "numpy==1.19.2",
        "pandas==1.1.3",
        "scipy==1.5.3",
        "scikit-learn==0.23.2",
        "imbalanced-learn==0.7.0",
        "sagemaker==2.117.0",
        "joblib==1.1.0",
    ]
)
print("Dependencies installed!")

import argparse

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import RandomForestClassifier

# Best Model Hyperparameters
BEST_PARAMS = {
    "max_depth": None,
    "min_samples_leaf": 5,
    "min_samples_split": 5,
    "n_estimators": 100,
    "random_state": 8,
}
SMOTE_SAMPLING_STRATEGY = 0.2
UNDERSAMPLING_STRATEGY = 0.7

# Parse input arguments (SageMaker provides `/opt/ml/input/data/training/`)
parser = argparse.ArgumentParser()
parser.add_argument("--train", type=str, default="/opt/ml/input/data/training/")
parser.add_argument(
    "--model_dir", type=str, default="/opt/ml/model/"
)  # SageMaker's default model directory
args = parser.parse_args()

# Check available files in the container
print(f"Checking files in {args.train}...")
available_files = os.listdir(args.train)
print(f"Available files: {available_files}")

# Load Training Data
X_train_path = os.path.join(args.train, "X_train.csv")
y_train_path = os.path.join(args.train, "y_train.csv")

print("Loading training data...")
X_train = pd.read_csv(X_train_path, header=None)
y_train = pd.read_csv(y_train_path, header=None).squeeze()  # Ensure 1D target array

# Debug: Print dataset shapes before preprocessing
print(f"X_train shape BEFORE resampling: {X_train.shape}")
print(f"y_train shape BEFORE resampling: {y_train.shape}")

# Apply SMOTE & Undersampling
print("Applying SMOTE and undersampling...")
smote = SMOTE(sampling_strategy=SMOTE_SAMPLING_STRATEGY, random_state=8)
undersample = RandomUnderSampler(
    sampling_strategy=UNDERSAMPLING_STRATEGY, random_state=8
)

X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
X_resampled, y_resampled = undersample.fit_resample(X_resampled, y_resampled)

# Train the Model
print("Training RandomForest model...")
model = RandomForestClassifier(**BEST_PARAMS)
model.fit(X_resampled, y_resampled)

# Save the trained model to SageMaker’s expected directory
os.makedirs(args.model_dir, exist_ok=True)
model_path = os.path.join(args.model_dir, "model.pkl")

joblib.dump(model, model_path)
print(f"Model trained and saved to {model_path}")
