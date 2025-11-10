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
DATA_DIR = BASE_DIR.parent / "data_collection" / "output" / "mater9"
TEXT_REPORTS_PATH = DATA_DIR / "text_reports_master.json"
STRUCTURED_REPORTS_PATH = DATA_DIR / "structured_english_reports_master.json"

# --- LỰA CHỌN MODEL EMBEDDING ---
# Đổi giá trị này thành "google" hoặc "hf" (HuggingFace)
# để chọn model bạn muốn dùng cho indexing và retrieval
EMBEDDING_CHOICE ="hf"  # <-- ĐỔI Ở ĐÂY

# --- Cấu hình cho Google (Gemini) ---
GOOGLE_EMBEDDING_MODEL_NAME = "models/text-embedding-004"
GOOGLE_VECTOR_STORE_DIR = str(BASE_DIR / "vector_store_google")

# --- Cấu hình cho HuggingFace (vietnamese-embedding) ---
HF_EMBEDDING_MODEL_NAME = "dangvantuan/vietnamese-embedding"
HF_VECTOR_STORE_DIR = str(BASE_DIR / "vector_store_hf")
HF_EMBEDDING_MAX_LENGTH = 256 # <-- RẤT QUAN TRỌNG: Thêm dòng này (lấy từ code của bạn)

# --- Cấu hình ChromaDB ---
# Dòng này đã được thêm lại
COLLECTION_NAME = "scholarships"

# --- Chunking ---
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 250