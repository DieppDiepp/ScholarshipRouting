"""
Module cấu hình cho Chatbot Thread 1
Quản lý các biến môi trường và cấu hình hệ thống
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load biến môi trường từ file .env (tìm ở root project)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

class Config:
    """Class chứa tất cả cấu hình của hệ thống"""
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR.parent / "data_collection" / "output" / "old12-official-FullMaster"
    TEXT_REPORTS_PATH = DATA_DIR / "text_reports_master.json"
    STRUCTURED_REPORTS_PATH = DATA_DIR / "structured_english_reports_master.json"
    
    # API Keys - Sử dụng đúng tên từ .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Từ .env: GEMINI_API_KEY
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Từ .env: TAVILY_API_KEY
    
    # Đường dẫn dữ liệu
    DATA_PATH = DATA_DIR / "structured_english_reports_master.json"
    RAG_DATABASE_PATH = DATA_DIR / "rag_database_master.jsonl"
    
    # Cấu hình Vector Database
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
    
    # Cấu hình Gemini - Sử dụng đúng tên từ .env
    # Model cho Intent Classification (nhanh)
    GEMINI_MODEL_CLASSIFICATION = os.getenv("GEMINI_MODEL_CLASSIFICATION", "gemini-2.5-flash-8b")
    # Model cho Response Generation (chất lượng)
    GEMINI_MODEL_GENERATION = os.getenv("GEMINI_MODEL_GENERATION", "gemini-2.5-flash")
    
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "3500"))
    
    # Cấu hình tìm kiếm - Sử dụng đúng giá trị từ .env
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
    TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", "3"))
    USE_SEMANTIC_SEARCH = os.getenv("USE_SEMANTIC_SEARCH", "false").lower() == "true"  # Bật/tắt Semantic Search
    
    @classmethod
    def _check_api_keys(cls, prefix: str) -> bool:
        """
        Kiểm tra xem có API keys nào không (single hoặc multiple)
        
        Args:
            prefix: 'GEMINI_API_KEY' hoặc 'TAVILY_API_KEY'
            
        Returns:
            True nếu có ít nhất 1 key
        """
        # Check single key format
        if os.getenv(prefix):
            return True
        
        # Check multiple keys format (PREFIX_1, PREFIX_2, ...)
        if prefix == "GEMINI_API_KEY":
            # Check GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, ...
            if os.getenv("GOOGLE_API_KEY_1"):
                return True
        elif prefix == "TAVILY_API_KEY":
            # Check TAVILY_API_KEY_1, TAVILY_API_KEY_2, ...
            if os.getenv("TAVILY_API_KEY_1"):
                return True
        
        return False
    
    @classmethod
    def validate(cls):
        """
        Kiểm tra tính hợp lệ của cấu hình
        Hỗ trợ cả single key và multiple keys format
        """
        # Check Gemini API keys
        if not cls._check_api_keys("GEMINI_API_KEY"):
            raise ValueError(
                "Không tìm thấy Gemini API key. Vui lòng cấu hình một trong các format sau:\n"
                "  - GEMINI_API_KEY=your-key (single key)\n"
                "  - GOOGLE_API_KEY_1=key1, GOOGLE_API_KEY_2=key2, ... (multiple keys)"
            )
        
        # Check Tavily API keys
        if not cls._check_api_keys("TAVILY_API_KEY"):
            raise ValueError(
                "Không tìm thấy Tavily API key. Vui lòng cấu hình một trong các format sau:\n"
                "  - TAVILY_API_KEY=your-key (single key)\n"
                "  - TAVILY_API_KEY_1=key1, TAVILY_API_KEY_2=key2, ... (multiple keys)"
            )
        
        return True

