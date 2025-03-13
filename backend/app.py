from fastapi import FastAPI
import uvicorn
import pandas as pd
import os
import joblib
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv
import sys

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import MODEL_STORAGE  # Import model storage paths from config.py

# Load environment variables
load_dotenv()

# Read port from environment variables (default: 8080)
PORT = int(os.getenv("PORT", 8080))

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

# Ensure model exists before loading
model_path = MODEL_STORAGE["model_pkl"]
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found at {model_path}. Ensure `evaluate_sagemaker.py` ran successfully!")

print(f"Loading model from {model_path}...")
model = joblib.load(model_path)
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

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)