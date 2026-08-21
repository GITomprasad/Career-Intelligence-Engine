# Multi-stage Python 3.11/3.12/3.14 slim image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY . .

# Generate dataset and train models
RUN python data/generate_datasets.py && python -m src.models.train_models

# Expose Streamlit and FastAPI ports
EXPOSE 8501
EXPOSE 8000

# Default command starts Streamlit web app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
