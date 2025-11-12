# Documentation

## Kiến trúc hệ thống

```
chatbot_thread1/
├── api/              # REST API
├── core/             # Core logic
│   ├── models/       # Data models
│   ├── modules/      # Intent router, Response generator
│   ├── tools/        # Search tools
│   └── utils/        # Utilities
├── test/             # Test cases
├── docs/             # Documentation
├── main.py           # Main chatbot
└── config.py         # Configuration
```

## Luồng xử lý

1. **Input** → User query
2. **Intent Classification** → Phân loại intent (7 loại)
3. **Tool Selection** → Chọn tools phù hợp
4. **Retrieval** → Lấy thông tin từ tools
5. **Context Assembly** → Tổng hợp context
6. **Response Generation** → Tạo câu trả lời
7. **Output** → Trả về kết quả

## Intent Types

### 1. fact_retrieval
Tìm chi tiết về học bổng cụ thể

**Tools:** Semantic Search (RAG)

**Example:** "Tell me about Turkiye Burslari"

### 2. filtering
Lọc/liệt kê học bổng theo tiêu chí

**Tools:** Structured Query

**Example:** "Show me scholarships in USA"

### 3. static_comparison
So sánh các học bổng

**Tools:** Structured Query

**Example:** "Compare Pearson and EGLS"

### 4. general_advice
Tư vấn chung về học bổng

**Tools:** Tavily Search

**Example:** "How to apply for scholarships?"

### 5. external_qa
Hỏi đáp ngoài luồng

**Tools:** Tavily Search

**Example:** "Cost of living in Singapore?"

### 6. personalized_advice
Tư vấn cá nhân hóa (cần profile)

**Tools:** Tavily Search + Profile Retriever

**Example:** "Do I have a good chance?"

### 7. personalized_recommendation
Đề xuất học bổng cá nhân (cần profile)

**Tools:** Structured Query + Profile Retriever

**Example:** "Which scholarship is best for me?"

## Core Modules

### IntentRouter
Phân loại intent từ query

**Input:** Query string, has_profile flag

**Output:** Intent object (type, confidence, params)

**Model:** Gemini API

### ResponseGenerator
Tạo câu trả lời từ context

**Input:** Query, context, intent

**Output:** Answer string

**Model:** Gemini API

**Timeout:** 60s per API call

## Tools

### SemanticSearchTool
Tìm kiếm semantic với RAG database

**Method:** Vector similarity (ChromaDB)

**Returns:** Top-K relevant documents

### StructuredQueryTool
Query dữ liệu có cấu trúc

**Methods:**
- `get_scholarship_details(name)` - Chi tiết học bổng
- `advanced_filter(filters)` - Lọc theo tiêu chí
- `compare_scholarships(names)` - So sánh

### TavilySearchTool
Tìm kiếm trên Internet

**API:** Tavily Search API

**Returns:** Web search results

### ProfileRetrieverTool
Xử lý profile người dùng

**Input:** User profile dict

**Output:** UserProfile object

## Configuration

### Environment Variables

```env
# API Keys
GEMINI_API_KEY=<key>
TAVILY_API_KEY=<key>

# Data
DATA_PATH=<path>
RAG_DATABASE_PATH=<path>

# Model
GEMINI_MODEL=models/gemini-2.5-flash
TEMPERATURE=0.3
MAX_TOKENS=2048

# Search
USE_SEMANTIC_SEARCH=false
TOP_K_RESULTS=3
TAVILY_MAX_RESULTS=3
```

### Timeout Settings

- **Chat timeout:** 180s (toàn bộ quá trình)
- **API call timeout:** 60s (mỗi Gemini call)
- **Context limit:** 8000 chars
- **Response limit:** 2048 tokens

## API Reference

### POST /api/chat

**Request:**
```json
{
  "query": "string",
  "profile_enabled": false,
  "user_profile": {
    "age": 22,
    "gpa": 3.5,
    "current_degree": "Bachelor",
    "field_of_study": "Computer Science"
  }
}
```

**Response:**
```json
{
  "query": "string",
  "answer": "string",
  "intent": "fact_retrieval",
  "confidence": 0.95,
  "tools_used": ["semantic_search"],
  "metadata": {
    "semantic_results_count": 3,
    "has_profile": false
  }
}
```

### GET /api/scholarships/search

**Query params:**
- `country` - Quốc gia
- `field` - Ngành học
- `degree` - Bậc học
- `funding` - Mức tài trợ

**Response:**
```json
{
  "scholarships": [...],
  "count": 10,
  "filters": {...}
}
```

## Testing

### Batch Testing

```bash
cd test
python run_batch_test.py
```

**Features:**
- Chạy test từ CSV files
- Giới hạn 1 sample/file (có thể thay đổi)
- Lưu kết quả ra CSV
- Hiển thị progress

### Test Structure

```
test/
├── test_case/        # CSV test cases
│   ├── Case 1.1 - Tìm chi tiết.csv
│   ├── Case 1.2 - Lọc liệt kê.csv
│   └── ...
└── test_results/     # Test results (ignored by git)
```

## Performance

### Response Time

- Intent classification: ~2-3s
- Retrieval: ~1-2s
- Response generation: ~3-5s
- **Total:** ~6-10s per query

## Troubleshooting

### Timeout ở static_comparison
✅ Fixed với timeout protection và giới hạn MAX_TOKENS=2048

### Response quá dài
Giảm MAX_TOKENS hoặc tối ưu prompt trong `response_generator.py`

### API rate limit
Thêm delay giữa các requests hoặc giảm TOP_K_RESULTS
