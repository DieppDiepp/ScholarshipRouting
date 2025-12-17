import os
from dotenv import load_dotenv
from pathlib import Path

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
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
DATA_DIR = BASE_DIR.parent / "data_collection" / "output" / "old12_full_levels"
TEXT_REPORTS_PATH = DATA_DIR / "text_reports.json"
STRUCTURED_REPORTS_PATH = DATA_DIR / "structured_english_reports.json"

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
INITIAL_K_RETRIEVAL = 200
# Số lượng học bổng duy nhất cuối cùng trả về
FINAL_K_RETRIEVAL = 5

# --- Cấu hình LLM ---
# Dùng cho các tác vụ không cần sáng tạo (bóc tách, phân loại)
EXTRACTOR_LLM_MODEL = "gemini-2.5-flash-lite"
EXTRACTOR_LLM_TEMP = 0.0

# Dùng cho các tác vụ sáng tạo (sinh câu trả lời - Phase 4)
GENERATOR_LLM_MODEL = "gemini-2.5-flash-lite"
GENERATOR_LLM_TEMP = 0.7

# Dùng cho dịch thuật
TRANSLATOR_LLM_MODEL = "gemini-2.5-flash-lite" # Dùng flash cho nhanh
TRANSLATOR_LLM_TEMP = 0.0

# 1. Định nghĩa cấu trúc (Schema)
class ScholarshipSearchFilters(BaseModel):
    Country: Optional[List[str]] = Field(
        None,
        description="The country the user wants to study in. Must always return a LIST of official country names. Example: ['UK'], ['USA', 'Canada'], ['China'], ['Hungary']"
    )
    Scholarship_Type: Optional[List[str]] = Field(
        None,
        description="The type (source) of the scholarship. Must always return a LIST of one or more of the following values: ['Government'], ['University'], ['Organization/Foundation']"
    )
    Funding_Level: Optional[List[str]] = Field(
        None,
        description="The funding level the user wants. Must always return a LIST of one or more of the following values: ['Full scholarship'], ['Tuition Waiver'], ['Stipend'], ['Accommodation'], ['Partial Funding'], ['Fixed Amount'], ['Other Costs']"
    )
    Required_Degree: Optional[str] = Field(
        None,
        description="The highest degree the user currently has (for filtering requirements). Must return ONLY ONE of the following values: 'High School Diploma','Bachelor', 'Master'"
    )
    Wanted_Degree:Optional[List[str]] = Field(
        None,
        description="The academic level the user wants to apply for. Must always return a LIST of one or more of the following values: ['Bachelor'], ['Master'], ['PhD']"
    )
    Eligible_Field_Group: Optional[List[str]] = Field(
        None,
        description="The field of study the user is interested in. Must always return a LIST. The LIST CAN ONLY INCLUDE values from the following: 'Education & Training', 'Arts, Design & Media', 'Humanities & Social Sciences', 'Economics & Business', 'Law & Public Policy', 'Natural Sciences', 'IT & Data Science', 'Engineering & Technology', 'Construction & Planning', 'Agriculture & Environment', 'Healthcare & Medicine', 'Social Services & Care', 'Personal Services & Tourism', 'Security & Defense', 'Library & Information Management', 'Transportation & Logistics', 'All fields'"
    )

class ScholarshipAnswer(BaseModel):
    scholarship_names: List[str] = Field(
        ..., 
        description="A list of the EXACT scholarship names found, e.g., ['Chevening Scholarship', 'CSC Scholarship']"
    )
    answer: str = Field(
        ..., 
        description="The final, synthesized, and friendly advisory answer for the user (in the user's original language)."
    )

# --- CẤU HÌNH CHO QUERY ROUTER (MỚI) ---
class QueryClassification(BaseModel):
    """
    Schema để LLM phân loại intent của user query.
    """
    query_type: Literal["greeting", "scholarship_search", "chitchat", "off_topic"] = Field(
        ...,
        description=(
            "The type of user query:\n"
            "- 'greeting': Greetings like 'hello', 'hi', 'xin chào', 'good morning'\n"
            "- 'scholarship_search': Questions about scholarships, studying abroad, funding, applications\n"
            "- 'chitchat': Casual conversation like 'how are you', 'cảm ơn bạn', 'that's great'\n"
            "- 'off_topic': Questions unrelated to scholarships (weather, news, math problems, etc.)"
        )
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation (1-2 sentences) of why this classification was chosen."
    )

# Config cho Router LLM (dùng flash cho nhanh)
ROUTER_LLM_MODEL = "gemini-2.5-flash-lite"
ROUTER_LLM_TEMP = 0.0

# python -m src.chatbot_thread2.rag_pipeline.indexing
# python -m src.chatbot_thread2.rag_pipeline.retriever
    