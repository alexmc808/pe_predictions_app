# PE Prediction App

## 📌 Overview
The **PE Prediction App** is a machine learning-based API designed to predict pulmonary embolism (PE) risk using patient data. The model is trained and deployed using **AWS SageMaker**, and the API is served via **FastAPI**.

## 🏗 Features
- Predicts PE risk from structured patient data.
- **AWS SageMaker** for model training and inference.
- Fetches trained models from **AWS S3**.
- Provides monitoring via **Prometheus** and **Grafana**.
- Fully containerized with **Docker** and managed using **Docker Compose**.

## 🔗 Technologies Used
- **Python 3.7**
- **FastAPI** - API framework
- **AWS SageMaker** - Model training & inference
- **AWS S3** - Model storage
- **Prometheus & Grafana** - Monitoring
- **Docker & Docker Compose** - Containerization