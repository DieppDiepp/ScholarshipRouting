# 1. Dùng Python base image
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir fastapi elasticsearch uvicorn firebase-admin prometheus-fastapi-instrumentator pydantic[email]

COPY . .

EXPOSE 8000


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
