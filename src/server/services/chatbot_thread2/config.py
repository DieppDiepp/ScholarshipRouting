import os
from dotenv import load_dotenv
from pathlib import Path

from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import sys

# Tải các biến môi trường từ file .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "chatbot.log"


# (Tránh trường hợp file bị kẹt)
if os.path.exists(LOG_FILE_PATH):
    os.remove(LOG_FILE_PATH)

# Tạo 2 handler (trình xử lý) riêng biệt
file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    # --- THÊM DÒNG NÀY ---
    # Ép buộc Python gỡ bỏ các handler cũ (của absl)
    # và sử dụng cấu hình này.
    force=True 
)

# --- Đường dẫn ---
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

# 1. Định nghĩa cấu trúc (Schema)
class ScholarshipSearchFilters(BaseModel):
    Country: Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Quốc gia mà người dùng muốn du học. Luôn trả về một DANH SÁCH (LIST) 1 hoặc nhiều tên quốc gia chính thức. Ví dụ: ['UK'], ['USA', 'Canada'], ['China'], ['Hungary']"
    )
    Scholarship_Type: Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Loại nguồn gốc học bổng. Luôn trả về DANH SÁCH (LIST) 1 hoặc nhiều giá trị sau: ['Government'], ['University'], ['Organization/Foundation']"
    )
    Funding_Level: Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Mức tài trợ. Luôn trả về DANH SÁCH (LIST) 1 hoặc nhiều giá trị sau: ['Full scholarship'], ['Tuition Waiver'], ['Stipend'], ['Accommodation'], ['Partial Funding'], ['Fixed Amount'], ['Other Costs']"
    )
    Required_Degree: Optional[str] = Field( # <-- GIỮ NGUYÊN (vì là '1 trong')
        None,
        description="Bằng tốt nghiệp cao nhất mà người dùng đang đề cập, chỉ chấp nhận trả về 1 TRONG các giá trị: 'High School Diploma','Bachelor', 'Master'"
    )
    Wanted_Degree:Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Bậc học mà người dùng muốn tìm. Luôn trả về DANH SÁCH 1 hoặc nhiều giá trị sau: ['Bachelor'], ['Master'], ['PhD']"
    )
    Eligible_Field_Group: Optional[List[str]] = Field(
        None,
        description="Nhóm ngành học người dùng quan tâm, Luôn trả về DANH SÁCH 1 hoặc nhiều giá trị, ví dụ: ['IT & Data Science'], ['Engineering & Technology', 'Natural Sciences']. DANH SÁCH CHỈ CÓ THỂ BAO GỒM CÁC GIÁ TRỊ: 'Education & Training', 'Arts, Design & Media', 'Humanities & Social Sciences', 'Economics & Business', 'Law & Public Policy', 'Natural Sciences', 'IT & Data Science', 'Engineering & Technology', 'Construction & Planning', 'Agriculture & Environment', 'Healthcare & Medicine', 'Social Services & Care', 'Personal Services & Tourism', 'Security & Defense', 'Library & Information Management', 'Transportation & Logistics', 'All fields'"
    )

class ScholarshipAnswer(BaseModel):
    scholarship_names: List[str] = Field(
        ..., 
        description="Danh sách CHÍNH XÁC tên các học bổng được tìm thấy, ví dụ: ['Chevening Scholarship', 'CSC Scholarship']"
    )
    answer: str = Field(
        ..., 
        description="Câu trả lời tổng hợp, thân thiện, tư vấn cho người dùng, viết bằng tiếng Việt."
    )

# python -m src.chatbot_thread2.rag_pipeline.indexing
# python -m src.chatbot_thread2.rag_pipeline.retriever
    