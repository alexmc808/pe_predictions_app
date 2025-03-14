"""
model_prep.py

This script prepares the dataset for machine learning by:
1. Removing unnecessary columns before preprocessing.
2. Splitting the data into train, validation, and test sets.
3. Applying standardization for numeric features and one-hot encoding for categorical features.
4. Keeping only the specified features.
5. Removing low-variance features.
6. Saving the processed datasets for modeling.

Usage:
    python scripts/model_prep.py
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import (ENGINEERED_FILES,  # Import file paths from config.py
                    MODEL_FILES)

# Ensure model_data directory exists
model_dir = os.path.dirname(MODEL_FILES["X_train"])
if not os.path.exists(model_dir):
    print(f"Creating directory: {model_dir}")
    os.makedirs(model_dir, exist_ok=True)

# Load Engineered Data
print("Loading engineered data...")
df = pd.read_csv(ENGINEERED_FILES["engineered"])

# Define Target Variable & Columns to Drop
target = "pe_outcome"
not_including = [
    "subject_id",
    "hadm_id_x",
    "dvt_date_x",
    "dvt_date_y",
    "pe_date",
    "dischtime",
    "pe_outcome",
    "length_of_stay",
    "dvt_icd_code",
    "dvt_icd_version",
    "dvt_diagnosis",
    "pe_icd_code",
    "pe_icd_version",
    "pe_diagnosis",
    "num_dvt_diagnoses",
    "hx_dvt",
    "num_pe_events",
]  # Excluding IDs, target, redundant, and non-modeled features

# Separate Features and Target
X = df.drop(columns=not_including, axis=1, errors="ignore")
y = df[[target]]

# Split Data Into Train, Validation, and Test Sets
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=8
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=8
)

# Identify Numeric and Categorical Features
numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()

# Define Preprocessing Pipeline (Standardization & One-Hot Encoding)
preprocessor = ColumnTransformer(
    [
        ("num", StandardScaler(), numeric_features),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse=False),
            categorical_features,
        ),  # Pass categorical_features
    ]
)

# Apply Pipeline to Training Data
print("Applying preprocessing pipeline...")
X_train_preprocessed = preprocessor.fit_transform(X_train)

# Manually Extract Feature Names for Older Sklearn Versions
num_feature_names = numeric_features
cat_feature_names = list(preprocessor.named_transformers_["cat"].categories_)

# Flatten categorical feature names (since categories_ is a list of lists)
cat_feature_names = [
    f"{col}_{val}"
    for col, vals in zip(categorical_features, cat_feature_names)
    for val in vals
]

# Combine Numeric and Categorical Feature Names
feature_names = num_feature_names + cat_feature_names

# Convert processed data into a DataFrame
X_train_preprocessed = pd.DataFrame(X_train_preprocessed, columns=feature_names)

# Apply Same Preprocessing to Validation & Test Sets
X_val_preprocessed = pd.DataFrame(preprocessor.transform(X_val), columns=feature_names)
X_test_preprocessed = pd.DataFrame(
    preprocessor.transform(X_test), columns=feature_names
)

# Define Final Selected Features After Encoding & Standardization
selected_features = [
    "race_grouped_White",
    "aids",
    "treatment_grouped_MT",
    "race_grouped_Unknown",
    "num_dvt_admissions",
    "hx_ac",
    "marital_status_Unknown",
    "hx_vte",
    "hx_pe",
    "admission_location_grouped_Referral-Based Admissions",
    "admission_location_grouped_Transfer from Another Facility",
    "insurance_Medicare",
    "treatment_grouped_Lytics",
    "cat_days_to_init_treatment_4-7 days",
    "race_grouped_Black",
    "treatment_grouped_Multiple Interventions",
    "cat_days_to_init_treatment_1-3 days",
    "had_ddimer",
    "discharge_location_grouped_Against Medical Advice",
    "race_grouped_Portuguese",
    "admission_location_grouped_Emergency/Urgent Care",
    "admission_location_grouped_Scheduled/Procedure-Based Admissions",
    "charlson_comorbidity_index",
]

# Ensure Only Available Features Are Selected
available_features = [
    col for col in selected_features if col in X_train_preprocessed.columns
]

if len(available_features) < len(selected_features):
    missing_features = set(selected_features) - set(available_features)
    print(
        f"Warning: The following selected features are missing and will be ignored: {missing_features}"
    )

# Filter Processed Data to Keep Only Selected Features
X_train_preprocessed = X_train_preprocessed[available_features]
X_val_preprocessed = X_val_preprocessed[available_features]
X_test_preprocessed = X_test_preprocessed[available_features]

# Variance-Based Feature Selection (Drop Low-Variance Features)
print("Identifying low-variance features...")
variance_threshold = 0.01
selector = VarianceThreshold(threshold=variance_threshold)
selector.fit(X_train_preprocessed)

# Identify Low-Variance Features to Drop
low_variance_features = X_train_preprocessed.columns[~selector.get_support()].tolist()
print(f"Low-Variance Features Identified: {len(low_variance_features)}")

# Drop Low-Variance Features
X_train_preprocessed.drop(columns=low_variance_features, inplace=True)
X_val_preprocessed.drop(columns=low_variance_features, inplace=True, errors="ignore")
X_test_preprocessed.drop(columns=low_variance_features, inplace=True, errors="ignore")

# Save Processed Data
print("Saving processed datasets...")
X_train_preprocessed.to_csv(MODEL_FILES["X_train"], index=False, header=False)
y_train.to_csv(MODEL_FILES["y_train"], index=False, header=False)

X_val_preprocessed.to_csv(MODEL_FILES["X_val"], index=False, header=False)
y_val.to_csv(MODEL_FILES["y_val"], index=False, header=False)

X_test_preprocessed.to_csv(MODEL_FILES["X_test"], index=False, header=False)
y_test.to_csv(MODEL_FILES["y_test"], index=False, header=False)

# Show Dataset Shapes
print("\nFinal Dataset Shapes:")
print(f"X_train: {X_train_preprocessed.shape}, y_train: {y_train.shape}")
print(f"X_val: {X_val_preprocessed.shape}, y_val: {y_val.shape}")
print(f"X_test: {X_test_preprocessed.shape}, y_test: {y_test.shape}")

print("Model preparation complete!")
