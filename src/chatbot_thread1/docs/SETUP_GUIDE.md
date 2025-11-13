# Setup Guide

## Yêu cầu hệ thống

- Python 3.8+
- pip
- Git

## Cài đặt

### 1. Clone repository

```bash
git clone <repo-url>
cd chatbot_thread1
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment

```bash
# Copy template
cp .env.example .env

# Chỉnh sửa .env
```

Điền các thông tin:

```env
# API Keys (BẮT BUỘC)
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Data paths
DATA_PATH=path/to/structured_english_reports_master.json
RAG_DATABASE_PATH=path/to/rag_database_master.jsonl

# Model settings
GEMINI_MODEL_CLASSIFICATION=gemini-2.5-flash-8b
GEMINI_MODEL_GENERATION=gemini-2.5-flash
TEMPERATURE=0.3
MAX_TOKENS=2048

# Search settings
USE_SEMANTIC_SEARCH=false
TOP_K_RESULTS=3
```

### 5. Lấy API Keys

**Gemini API:**
1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập Google
3. Click "Create API Key"
4. Copy key vào .env

**Tavily API:**
1. Truy cập: https://tavily.com/
2. Đăng ký tài khoản
3. Copy API key vào .env

### 6. Chuẩn bị dữ liệu

Đảm bảo có 2 file:
- `structured_english_reports_master.json` - Dữ liệu học bổng
- `rag_database_master.jsonl` - RAG database

Cập nhật đường dẫn trong `.env`

### 7. Kiểm tra cài đặt

```bash
python scripts/check_setup.py
```

## Chạy ứng dụng

### Interactive Mode

```bash
python main.py
```

### API Server

**Flask (port 5000):**
```bash
python api/api_flask.py
```

**FastAPI (port 8000):**
```bash
python api/api_fastapi.py
```

### Batch Testing

```bash
cd test
python run_batch_test.py
```
