"""
Module cấu hình cho Chatbot Thread 1
Quản lý các biến môi trường và cấu hình hệ thống
"""
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

class Config:
    """Class chứa tất cả cấu hình của hệ thống"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Đường dẫn dữ liệu
    DATA_PATH = os.getenv("DATA_PATH", "../data_collection/output/mater9/structured_english_reports_master.json")
    RAG_DATABASE_PATH = os.getenv("RAG_DATABASE_PATH", "../data_collection/output/mater9/rag_database_master.jsonl")
    
    # Cấu hình Vector Database
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-004")
    
    # Cấu hình Gemini
    # Model cho Intent Classification (nhanh)
    GEMINI_MODEL_CLASSIFICATION = os.getenv("GEMINI_MODEL_CLASSIFICATION", "models/gemini-2.5-flash")
    # Model cho Response Generation (chất lượng)
    GEMINI_MODEL_GENERATION = os.getenv("GEMINI_MODEL_GENERATION", "models/gemini-2.5-flash")
    
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    
    # Cấu hình tìm kiếm
    TOP_K_RESULTS = 3  
    TAVILY_MAX_RESULTS = 2  
    USE_SEMANTIC_SEARCH = os.getenv("USE_SEMANTIC_SEARCH", "true").lower() == "true"  # Bật/tắt Semantic Search
    
    @classmethod
    def validate(cls):
        """Kiểm tra tính hợp lệ của cấu hình"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong file .env")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY chưa được cấu hình trong file .env")
        return True
