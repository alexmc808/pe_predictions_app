# Use Python 3.7 as the base image
FROM python:3.7

# Set the working directory inside the container
WORKDIR /app

# Copy only necessary files
COPY requirements.txt .
COPY app.py .
COPY config.py .
COPY model.pkl .
COPY model.tar.gz .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI runs on
EXPOSE 8080

# Run FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]