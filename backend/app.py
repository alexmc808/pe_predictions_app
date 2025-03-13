from fastapi import FastAPI
import uvicorn
import pandas as pd
import os
import tarfile
import joblib
import time
import boto3
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Load environment variables from .env file (if running locally)
load_dotenv()

# AWS Configuration (read from environment variables)
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
MODEL_KEY = os.getenv("MODEL_KEY")

# Ensure environment variables are set
if not all([AWS_REGION, S3_BUCKET, MODEL_KEY]):
    raise EnvironmentError("Missing AWS environment variables! Ensure AWS_REGION, S3_BUCKET, and MODEL_KEY are set.")

# Define model paths
MODEL_TAR_PATH = "model.tar.gz"  # Downloaded model archive
MODEL_PKL_PATH = "model.pkl"  # Extracted model file

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Prometheus Metrics
REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Latency of API requests", ["method", "endpoint"])

# Middleware for Monitoring API Calls
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

        return response

def download_and_extract_model():
    """ Download and extract model from S3 """
    
    # Download if not already present
    if not os.path.exists(MODEL_PKL_PATH):
        print(f"Downloading model from s3://{S3_BUCKET}/{MODEL_KEY}...")
        s3_client.download_file(S3_BUCKET, MODEL_KEY, MODEL_TAR_PATH)
        print("Model downloaded successfully.")

        print("Extracting model archive...")
        with tarfile.open(MODEL_TAR_PATH, "r:gz") as tar:
            members = [m for m in tar.getmembers() if m.name.endswith("model.pkl")]
            if not members:
                raise FileNotFoundError("❌ Model file not found in archive. Check S3 contents!")
            tar.extract(members[0], path=".")  # Extract directly in backend
            extracted_model_name = members[0].name

        # Rename extracted model to MODEL_PKL_PATH
        os.rename(extracted_model_name, MODEL_PKL_PATH)
        print(f"Model successfully extracted and renamed to {MODEL_PKL_PATH}")

    else:
        print(f"Model already exists: {MODEL_PKL_PATH}")

# Ensure model is downloaded and extracted
download_and_extract_model()

# Load Model
print(f"Loading model from {MODEL_PKL_PATH}...")
model = joblib.load(MODEL_PKL_PATH)
print("Model loaded successfully!")

# Extract expected feature names from the model
if hasattr(model, "feature_names_in_"):  # scikit-learn >= 1.0
    expected_features = list(model.feature_names_in_)
elif hasattr(model, "n_features_in_"):  # scikit-learn < 1.0
    expected_features = [str(i) for i in range(model.n_features_in_)]
else:
    raise ValueError("Unable to determine expected feature names from the model!")

print(f"Expected feature names: {expected_features}")

# Initialize FastAPI
app = FastAPI()
app.add_middleware(MetricsMiddleware)  # Add Prometheus Middleware

@app.get("/")
def home():
    return {"message": "Machine Learning API is running!"}

@app.get("/metrics")
def metrics():
    """ Exposes Prometheus metrics """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict/")
def predict(data: dict):
    """ Receive JSON input, convert to DataFrame, and make a prediction """
    
    df = pd.DataFrame([data])

    # Ensure input data matches expected features
    if set(df.columns) != set(expected_features):
        return {
            "error": "Feature names do not match model expectations",
            "received": df.columns.tolist(),
            "expected": expected_features
        }

    # Reorder features before prediction
    df = df[expected_features]

    # Make prediction
    prediction = model.predict(df)

    return {"prediction": int(prediction[0])}  # Return the result

# Read port from environment variables (default: 8080)
PORT = int(os.getenv("PORT", 8080))

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)