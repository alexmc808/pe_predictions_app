"""
preprocessing.py

This script performs data preprocessing for the pe_predictions_app project. 
It loads raw datasets, merges them into a single dataframe, handles missing 
values, applies transformations, and saves the cleaned dataset for modeling.

Key Steps:
1. Load raw data from CSV files.
2. Merge data from different sources into a single dataset.
3. Convert data types and handle missing values.
4. Create categorical features for better model interpretation.
5. Save preprocessed datasets for downstream modeling.

Usage:
Run this script from the command line or another Python script:
    python scripts/preprocessing.py

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import RAW_FILES, PROCESSED_FILES

# Set pandas display options
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 0)
pd.set_option("display.float_format", "{:.2f}".format)

# Load Data
print("Loading data...")
comorbidities = pd.read_csv(RAW_FILES["comorbidities"])
diagnosis = pd.read_csv(RAW_FILES["diagnosis"])
labs = pd.read_csv(RAW_FILES["labs"])
treatments = pd.read_csv(RAW_FILES["treatments"])

# Merge Data
print("Merging data...")
df = (
    diagnosis
    .merge(comorbidities, on=["subject_id", "hadm_id"], how="left")
    .merge(labs[["subject_id", "had_ddimer", "had_o2_sat"]], on="subject_id", how="inner")
    .merge(treatments, on="subject_id", how="left")
)

# Convert Data Types
print("Converting data types...")
df["dvt_icd_version"] = df["dvt_icd_version"].astype("object")
df["pe_icd_version"] = df["pe_icd_version"].astype("object")

# Ensure Subject-Level Data
print("Ensuring unique subjects...")
df["num_pe_events"] = df.groupby("subject_id")["pe_outcome"].sum()
df = df.sort_values(by=["subject_id", "pe_date"]).drop_duplicates(subset="subject_id", keep="first")

# Handle Missing Values
print("Handling missing values...")
df["discharge_location"].fillna("Unknown", inplace=True)
df["insurance"].fillna("Unknown", inplace=True)
df["marital_status"].fillna("Unknown", inplace=True)

df["pe_icd_code"].fillna("No PE", inplace=True)
df["pe_icd_version"].fillna("No PE", inplace=True)
df["pe_diagnosis"].fillna("No PE", inplace=True)

# Create `days_to_init_treatment`
print("Creating 'days_to_init_treatment'...")
treatment_days = ["days_to_ac", "days_to_lytics", "days_to_mt", "days_to_cdt"]
df['days_to_init_treatment'] = df[treatment_days].min(axis = 1, skipna = True)

# Categorize `days_to_init_treatment`
print("Categorizing treatment times...")
bins = [-0.1, 0, 3, 7, df["days_to_init_treatment"].max()]
labels = ["Same day", "1-3 days", "4-7 days", "More than 7 days"]
df["cat_days_to_init_treatment"] = pd.cut(df["days_to_init_treatment"], bins=bins, labels=labels)

# Ensure "No Treatment" is a valid category
df["cat_days_to_init_treatment"] = df["cat_days_to_init_treatment"].astype("category")
df["cat_days_to_init_treatment"] = df["cat_days_to_init_treatment"].cat.add_categories("No Treatment")

# Fill in NaN values with "No Treatment"
df["cat_days_to_init_treatment"].fillna("No Treatment", inplace=True)

# Drop Unnecessary Columns
print("Dropping unnecessary columns...")
df.drop(columns=["days_to_ac", "days_to_lytics", "days_to_mt", "days_to_cdt", "days_to_init_treatment"], inplace=True)

# Filter Out Expired Patients
print("Filtering expired patients...")
expired = df[((df["hospital_expire_flag"] == 1) | (df["discharge_location"] == "DIED")) & df["days_to_pe"].isna()]
df = df[(df["hospital_expire_flag"] == 0) & (df["discharge_location"] != "DIED")]

# Save Processed Data
# Ensure processed directory exists before saving
processed_dir = os.path.dirname(PROCESSED_FILES["preprocessed"])
if not os.path.exists(processed_dir):
    print(f"Creating directory: {processed_dir}")
    os.makedirs(processed_dir, exist_ok=True)
print(f"Saving processed data to {PROCESSED_FILES['preprocessed']}...")
df.to_csv(PROCESSED_FILES["preprocessed"], index=False)
print("Preprocessing complete!")