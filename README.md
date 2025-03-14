# **PE Prediction App**

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
- **GitHub Actions** - CI/CD Automation

## 🚀 **Setup & Deployment Guide**
This guide will walk you through deploying the PE Prediction App on an **AWS EC2 instance**.

### **1️⃣ Launch an EC2 Instance**
- **Instance Type:** `t2.micro` (Free Tier eligible)
- **AMI:** Ubuntu 22.04 LTS
- **Security Group:** Allow **all inbound traffic (IPv4)**
  - Port `8080` → API endpoint
  - Port `9090` → Prometheus
  - Port `3000` → Grafana

### **2️⃣ Connect to EC2 Instance**
Use **PuTTY** (Windows) or **SSH** (Mac/Linux) to connect:
```sh
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### **3️⃣ Install Dependencies & Clone the Repository**
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install -y git
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo apt install -y docker-compose

# Clone the repository
git clone https://github.com/alexmc808/pe_predictions_app.git
cd pe_predictions_app/backend
```

### **4️⃣ Build & Run the Docker Container**
```sh
sudo docker build -t pe-prediction-app .
sudo docker-compose up --build
```
- This will pull the trained model from **AWS S3**, extract it, and start the FastAPI service.
- The app will run on `http://<EC2_PUBLIC_IP>:8080`.

To stop the app, run:
```sh
sudo docker-compose down
```

## 🛠 **Testing the API**
Once the app is running, you can test predictions using `curl`:

```sh
curl -X 'POST' \
  'http://<EC2_PUBLIC_IP>:8080/predict/' \
  -H 'Content-Type: application/json' \
  -d '{
    "0": 1,
    "1": 0,
    "2": 0,
    "3": 0.693,
    "4": 1,
    "5": 0,
    "6": 1,
    "7": 0,
    "8": 0,
    "9": 1,
    "10": 1,
    "11": 0,
    "12": 0,
    "13": 0,
    "14": 1,
    "15": 1,
    "16": 1,
    "17": 0,
    "18": 3
  }'
```
Expected Response:
```json
{"prediction": 1}
```

## 📊 **Monitoring with Prometheus & Grafana**
Once deployed, monitoring is available:
- **Prometheus:** `http://<EC2_PUBLIC_IP>:9090/metrics`
- **Grafana:** `http://<EC2_PUBLIC_IP>:3000`

> **🔹 Default Grafana login:**  
> **Username:** `admin`  
> **Password:** `admin`

## 🔄 **Updating the App**
To pull the latest changes and restart:
```sh
git pull origin main
sudo docker-compose up --build
```