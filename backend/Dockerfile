FROM python:3.12.10-slim-bullseye

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU version and ONNX dependencies
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install optimum onnxruntime onnx scipy --no-deps

# Copy the conversion script
COPY convert_to_onnx.py .

# Copy source code
COPY main.py .
COPY src src

# Run conversion script
RUN python convert_to_onnx.py

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
