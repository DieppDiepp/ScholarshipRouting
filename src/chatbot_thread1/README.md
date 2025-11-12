# Scholarship Chatbot

Chatbot tư vấn học bổng quốc tế sử dụng AI với Intent Routing và Multi-Tool Retrieval.

## Tính năng

- Phân loại 7 loại intent tự động
- Kết hợp Semantic Search, Structured Query và Tavily Search
- Đề xuất học bổng dựa trên profile người dùng
- REST API (Flask & FastAPI)
- Timeout protection (180s)

## Cài đặt

```bash
# Clone repo
git clone <your-repo-url>
cd chatbot_thread1

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình
cp .env.example .env
# Chỉnh sửa .env và điền API keys
```

## API Keys

- **GEMINI_API_KEY**: https://makersuite.google.com/app/apikey
- **TAVILY_API_KEY**: https://tavily.com/

## Sử dụng

**Interactive Mode:**
```bash
python main.py
```

**Flask API (port 5000):**
```bash
python api/api_flask.py
```

**FastAPI (port 8000):**
```bash
python api/api_fastapi.py
# Docs: http://localhost:8000/docs
```

**Batch Testing:**
```bash
cd test
python run_batch_test.py
```

## API Endpoints

- `POST /api/chat` - Chat với bot
- `GET /api/scholarships/countries` - Danh sách quốc gia
- `GET /api/scholarships/fields` - Danh sách ngành học
- `GET /api/scholarships/search` - Tìm kiếm học bổng
- `GET /api/scholarships/{name}` - Chi tiết học bổng

## Intent Types

1. `fact_retrieval` - Tìm chi tiết học bổng
2. `filtering` - Lọc/liệt kê học bổng
3. `static_comparison` - So sánh học bổng
4. `general_advice` - Tư vấn chung
5. `external_qa` - Hỏi đáp ngoài luồng
6. `personalized_advice` - Tư vấn cá nhân
7. `personalized_recommendation` - Đề xuất cá nhân

## Cấu hình

File `.env`:
- `MAX_TOKENS=2048` - Giới hạn response
- `TEMPERATURE=0.3` - Độ sáng tạo (0.0-1.0)
- `USE_SEMANTIC_SEARCH=false` - Bật/tắt semantic search
