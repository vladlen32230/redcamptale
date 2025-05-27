FROM python:3.12.10-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .
COPY src src

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
