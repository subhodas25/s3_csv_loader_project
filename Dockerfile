#FROM registry.access.redhat.com/ubi9/python-3.11
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY config/ config/

EXPOSE 8000
CMD ["python", "-m", "app.ingest"]
