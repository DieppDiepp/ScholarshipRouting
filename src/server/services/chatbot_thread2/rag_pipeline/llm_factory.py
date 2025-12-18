import os
import itertools
from typing import List, Iterator, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import logging

from .. import config

logger = logging.getLogger(__name__)

# ==========================================
# 1. QUẢN LÝ KEY GOOGLE (Cho Embedding & Gemini)
# ==========================================
def _load_google_api_keys() -> List[str]:
    """
    Tải tất cả các key GOOGLE_API_KEY_...
    """
    keys = []
    SCAN_RANGE = 50 
    
    # Chỉ log quét nếu đang dùng Google
    if config.LLM_PROVIDER == "google" or config.EMBEDDING_CHOICE == "google":
        logger.info(f"--- LLM Factory: Quét key Google từ 1 đến {SCAN_RANGE}... ---")

    for i in range(1, SCAN_RANGE + 1):
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if key and key.strip():
            keys.append(key.strip())
            
    if not keys:
        if config.LLM_PROVIDER == "google" or config.EMBEDDING_CHOICE == "google":
             logger.warning("Cảnh báo: Không tìm thấy GOOGLE_API_KEY nào, nhưng đang được cấu hình để sử dụng!")
    else:
        # Chỉ log số lượng nếu tìm thấy
        if config.LLM_PROVIDER == "google" or config.EMBEDDING_CHOICE == "google":
            logger.info(f"--- LLM Factory: Đã tải {len(keys)} Google API keys ---")
    return keys

# Khởi tạo Pool
GOOGLE_KEY_POOL = _load_google_api_keys()
# Tạo cycler an toàn
if GOOGLE_KEY_POOL:
    _google_key_cycler = itertools.cycle(range(len(GOOGLE_KEY_POOL)))
else:
    _google_key_cycler = None

def get_next_google_key() -> str:
    """
    Dùng cho Indexing (Embedding) và Chatbot (nếu Provider = google)
    """
    if not _google_key_cycler:
        raise ValueError("Google Key Pool is empty! Kiểm tra file .env")
        
    idx = next(_google_key_cycler)
    key = GOOGLE_KEY_POOL[idx]
    # logger.info(f"--- LLM FACTORY (Google): Using Key #{idx + 1} ---")
    return key


# ==========================================
# 2. QUẢN LÝ KEY OPENAI (Cho Chatbot - Text Gen)
# ==========================================
def _load_openai_api_keys() -> List[str]:
    keys = []
    SCAN_RANGE = 50 
    
    if config.LLM_PROVIDER == "openai":
        logger.info(f"--- LLM Factory: Quét key OpenAI từ 1 đến {SCAN_RANGE}... ---")

    for i in range(1, SCAN_RANGE + 1):
        key = os.getenv(f"OPENAI_API_KEY_{i}")
        if key and key.strip():
            keys.append(key.strip())
            
    if config.LLM_PROVIDER == "openai" and not keys:
        raise ValueError("Cấu hình dùng OpenAI nhưng không tìm thấy OPENAI_API_KEY trong .env")
    
    if keys and config.LLM_PROVIDER == "openai":
        logger.info(f"--- LLM Factory: Đã tải {len(keys)} OpenAI API keys ---")
    
    return keys

OPENAI_KEY_POOL = _load_openai_api_keys()
if OPENAI_KEY_POOL:
    _openai_key_cycler = itertools.cycle(range(len(OPENAI_KEY_POOL)))
else:
    _openai_key_cycler = None

def get_next_openai_key() -> str:
    if not _openai_key_cycler:
        raise ValueError("OpenAI Key Pool is empty!")
    idx = next(_openai_key_cycler)
    key = OPENAI_KEY_POOL[idx]
    logger.info(f"--- LLM FACTORY (OpenAI): Using Key #{idx + 1} ---")
    return key


# ==========================================
# 3. FACTORY FUNCTIONS (ĐÃ KHÔI PHỤC LOGIC PROVIDER)
# ==========================================

def get_translator_llm():
    if config.LLM_PROVIDER == "openai":
        api_key = get_next_openai_key()
        return ChatOpenAI(
            model=config.OPENAI_LITE_MODEL,
            api_key=api_key,
            temperature=config.TRANSLATOR_LLM_TEMP
        )
    else:
        api_key = get_next_google_key()
        return ChatGoogleGenerativeAI(
            model=config.TRANSLATOR_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.TRANSLATOR_LLM_TEMP
        )

def get_extractor_llm():
    if config.LLM_PROVIDER == "openai":
        api_key = get_next_openai_key()
        llm = ChatOpenAI(
            model=config.OPENAI_LITE_MODEL,
            api_key=api_key,
            temperature=config.EXTRACTOR_LLM_TEMP
        )
    else:
        api_key = get_next_google_key()
        llm = ChatGoogleGenerativeAI(
            model=config.EXTRACTOR_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.EXTRACTOR_LLM_TEMP
        )
    
    return llm.with_structured_output(config.ScholarshipSearchFilters)

def get_generator_llm():
    if config.LLM_PROVIDER == "openai":
        api_key = get_next_openai_key()
        llm = ChatOpenAI(
            model=config.OPENAI_HEAVY_MODEL,
            api_key=api_key,
            temperature=config.GENERATOR_LLM_TEMP
        )
    else:
        api_key = get_next_google_key()
        llm = ChatGoogleGenerativeAI(
            model=config.GENERATOR_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.GENERATOR_LLM_TEMP
        )
        
    return llm.with_structured_output(config.ScholarshipAnswer)