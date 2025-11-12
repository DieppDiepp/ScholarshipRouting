import os
from dotenv import load_dotenv
from pathlib import Path

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY không được tìm thấy trong file .env")

# --- Đường dẫn ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data_collection" / "output" / "old12-official-FullMaster"
TEXT_REPORTS_PATH = DATA_DIR / "text_reports_master.json"
STRUCTURED_REPORTS_PATH = DATA_DIR / "structured_english_reports_master.json"

# --- LỰA CHỌN MODEL EMBEDDING ---
# Đổi giá trị này thành "google" hoặc "hf" (HuggingFace)
# để chọn model bạn muốn dùng cho indexing và retrieval
EMBEDDING_CHOICE ="google"  # <-- ĐỔI Ở ĐÂY

# --- Cấu hình cho Google (Gemini) ---
GOOGLE_EMBEDDING_MODEL_NAME = "models/text-embedding-004"
GOOGLE_VECTOR_STORE_DIR = str(BASE_DIR / "vector_store_google")

# --- Cấu hình cho HuggingFace (vietnamese-embedding) ---
HF_EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
HF_VECTOR_STORE_DIR = str(BASE_DIR / "vector_store_hf")
# Dòng này thay đổi: (max length của model E5)
HF_EMBEDDING_MAX_LENGTH = 512

# --- Cấu hình ChromaDB ---
COLLECTION_NAME = "scholarships"

# --- Chunking ---
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 250

# --- CẤU HÌNH RAG RETRIEVAL (MỚI) ---
# Số lượng chunk ban đầu để semantic search
INITIAL_K_RETRIEVAL = 100
# Số lượng học bổng duy nhất cuối cùng trả về
FINAL_K_RETRIEVAL = 5

# --- Cấu hình LLM ---
# Dùng cho các tác vụ không cần sáng tạo (bóc tách, phân loại)
EXTRACTOR_LLM_MODEL = "gemini-2.5-flash"
EXTRACTOR_LLM_TEMP = 0.0

# Dùng cho các tác vụ sáng tạo (sinh câu trả lời - Phase 4)
GENERATOR_LLM_MODEL = "gemini-2.5-flash"
GENERATOR_LLM_TEMP = 0.7

# Dùng cho dịch thuật
TRANSLATOR_LLM_MODEL = "gemini-2.5-flash-lite" # Dùng flash cho nhanh
TRANSLATOR_LLM_TEMP = 0.0

# python -m src.chatbot_thread2.rag_pipeline.retriever
    