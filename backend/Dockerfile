FROM python:3.12.10-slim-bullseye

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libicu-dev \
        pkg-config \
        g++ \
        make \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install all dependencies including PyTorch and ONNX in one step
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir optimum onnxruntime onnx

# Set environment variable for model preloading
ENV STANDARD_CLASSIFIER_NAME=MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli

# Copy build script and run it to download and convert model to ONNX
COPY build_model.py .
RUN python build_model.py

# Copy source code
COPY main.py .
COPY src src

EXPOSE 8080

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "main:app"]
