"""
engineering.py

This script performs feature engineering on the preprocessed dataset. 
It applies transformations, creates new features, and prepares the final dataset for modeling.

Key Steps:
1. Load the preprocessed dataset.
2. Create categorical and numerical features.
3. Consolidate related features.
4. Remove unnecessary fields.
5. Save the engineered dataset.

Usage:
Run this script as:
    python scripts/engineering.py
"""

import pandas as pd
import numpy as np
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PROCESSED_FILES, ENGINEERED_FILES

# Load Preprocessed Data
print("Loading preprocessed data...")
df = pd.read_csv(PROCESSED_FILES["preprocessed"])

# Convert Data Types
print("Converting data types...")
df["dvt_icd_version"] = df["dvt_icd_version"].astype("object")

# Create `treatment_grouped` Field
print("Creating treatment group categories...")

# Define treatment labels
treatment_labels = {
    "ac_flag": "AC",
    "lytics_flag": "Lytics",
    "mt_flag": "MT",
    "us_cdt_flag": "CDT"
}

# Create treatment column by joining multiple active treatments
df["treatment"] = df.apply(lambda row: ", ".join([name for col, name in treatment_labels.items() if row[col] == 1]), axis=1)

# Consolidate treatment categories
def consolidate_treatment(treatment):
    if pd.isna(treatment) or treatment.strip() == "":
        return "No Treatment"
    elif treatment == "AC":
        return "AC Only"
    elif "MT" in treatment and "CDT" in treatment:
        return "Multiple Interventions"
    elif "Lytics" in treatment and "MT" not in treatment and "CDT" not in treatment:
        return "Lytics"
    elif "MT" in treatment and "CDT" not in treatment:
        return "MT"
    elif "CDT" in treatment and "MT" not in treatment:
        return "CDT"
    else:
        return "Other"

# Apply the function to create a new consolidated column
df["treatment_grouped"] = df["treatment"].apply(consolidate_treatment)

# Consolidate `race` Field
print("Consolidating race categories...")

race_mapping = {
    "BLACK/AFRICAN AMERICAN": "Black",
    "BLACK/CARIBBEAN ISLAND": "Black",
    "BLACK/CAPE VERDEAN": "Black",
    "BLACK/AFRICAN": "Black",
    
    "WHITE": "White",
    "WHITE - OTHER EUROPEAN": "White",
    "WHITE - EASTERN EUROPEAN": "White",
    "WHITE - RUSSIAN": "White",
    "WHITE - BRAZILIAN": "White",

    "ASIAN": "Asian",
    "ASIAN - CHINESE": "Asian",
    "ASIAN - KOREAN": "Asian",
    "ASIAN - SOUTH EAST ASIAN": "Asian",
    "ASIAN - ASIAN INDIAN": "Asian",

    "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER": "Native Hawaiian/Pacific Islander",
    "AMERICAN INDIAN/ALASKA NATIVE": "American Indian/Alaska Native",

    "HISPANIC OR LATINO": "Hispanic/Latino",
    "HISPANIC/LATINO - CENTRAL AMERICAN": "Hispanic/Latino",
    "HISPANIC/LATINO - PUERTO RICAN": "Hispanic/Latino",
    "HISPANIC/LATINO - DOMINICAN": "Hispanic/Latino",
    "HISPANIC/LATINO - GUATEMALAN": "Hispanic/Latino",
    "HISPANIC/LATINO - COLUMBIAN": "Hispanic/Latino",
    "HISPANIC/LATINO - MEXICAN": "Hispanic/Latino",
    "HISPANIC/LATINO - CUBAN": "Hispanic/Latino",
    "HISPANIC/LATINO - SALVADORAN": "Hispanic/Latino",
    "HISPANIC/LATINO - HONDURAN": "Hispanic/Latino",
    "SOUTH AMERICAN": "Hispanic/Latino",

    "PORTUGUESE": "Portuguese",
    "MULTIPLE RACE/ETHNICITY": "Multiracial",
    
    "UNKNOWN": "Unknown",
    "UNABLE TO OBTAIN": "Unknown",
    "PATIENT DECLINED TO ANSWER": "Unknown",
    "OTHER": "Unknown"
}

df["race_grouped"] = df["race"].map(race_mapping)

# Consolidate `discharge_location`
print("Grouping discharge locations...")

discharge_location_mapping = {
    "HOME": "Home/Community-Based Care",
    "HOME HEALTH CARE": "Home/Community-Based Care",
    "ASSISTED LIVING": "Home/Community-Based Care",
    
    "SKILLED NURSING FACILITY": "Facility-Based Care",
    "CHRONIC/LONG TERM ACUTE CARE": "Facility-Based Care",
    "REHAB": "Facility-Based Care",
    "HOSPICE": "Facility-Based Care",
    "PSYCH FACILITY": "Facility-Based Care",
    "ACUTE HOSPITAL": "Facility-Based Care",
    "OTHER FACILITY": "Facility-Based Care",
    "HEALTHCARE FACILITY": "Facility-Based Care",
    
    "AGAINST ADVICE": "Against Medical Advice",
    
    "Unknown": "Unknown"
}

df["discharge_location_grouped"] = df["discharge_location"].map(discharge_location_mapping)

# Consolidate `admission_location`
print("Grouping admission locations...")

admission_location_mapping = {
    "EMERGENCY ROOM": "Emergency/Urgent Care",
    "WALK-IN/SELF REFERRAL": "Emergency/Urgent Care",

    "PHYSICIAN REFERRAL": "Referral-Based Admissions",
    "CLINIC REFERRAL": "Referral-Based Admissions",

    "TRANSFER FROM HOSPITAL": "Transfer from Another Facility",
    "TRANSFER FROM SKILLED NURSING FACILITY": "Transfer from Another Facility",
    "AMBULATORY SURGERY TRANSFER": "Transfer from Another Facility",
    "INTERNAL TRANSFER TO OR FROM PSYCH": "Transfer from Another Facility",

    "PROCEDURE SITE": "Scheduled/Procedure-Based Admissions",
    "PACU": "Scheduled/Procedure-Based Admissions",

    "INFORMATION NOT AVAILABLE": "Unknown"
}

df["admission_location_grouped"] = df["admission_location"].map(admission_location_mapping)

# Drop Unnecessary Columns
print("Dropping unnecessary columns...")
df = df.drop(columns=["race", "admission_type", "admission_location", "discharge_location", 
                      "ac_flag", "lytics_flag", "mt_flag", "us_cdt_flag", "treatment"], axis=1)

# Save Engineered Data
# Ensure engineered directory exists before saving
engineered_dir = os.path.dirname(ENGINEERED_FILES["engineered"])
if not os.path.exists(engineered_dir):
    print(f"Creating directory: {engineered_dir}")
    os.makedirs(engineered_dir, exist_ok=True)
print(f"Saving engineered data to {ENGINEERED_FILES['engineered']}...")
df.to_csv(ENGINEERED_FILES["engineered"], index=False)
print("Feature engineering complete!")