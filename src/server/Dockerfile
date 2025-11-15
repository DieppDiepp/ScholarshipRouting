# 1. Dùng Python base image
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi elasticsearch uvicorn firebase-admin prometheus-fastapi-instrumentator pydantic[email] \
    numpy pandas pyarrow fastparquet \
    ipykernel ipython openpyxl docling \
    langchain langchain-core langchain-community \
    langsmith python-dotenv langgraph langchain-tavily \
    langchain-google-genai langchain_community langchain_chroma \
    langchain-text-splitters tqdm google-generativeai ==0.8.5
    # sentence-transformers langchain-huggingface transformers torch
COPY . .

EXPOSE 8000


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
