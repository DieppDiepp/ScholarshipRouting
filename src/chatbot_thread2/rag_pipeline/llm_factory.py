import os
import itertools
from typing import List, Iterator
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

from .. import config

# Lấy logger
logger = logging.getLogger(__name__)

def _load_api_keys() -> List[str]:
    """
    Tải tất cả các key có dạng GOOGLE_API_KEY_... từ file .env
    Sử dụng vòng lặp FOR để quét, chấp nhận các số thứ tự bị đứt quãng.
    (Ví dụ: Có Key 2, Key 5 nhưng thiếu Key 1, Key 3, 4 vẫn chạy tốt)
    """
    keys = []
    # Quét thử từ 1 đến 50 (hoặc 100 tùy bạn)
    # Nếu key 1 bị comment, nó sẽ bỏ qua và check tiếp key 2
    SCAN_RANGE = 50 
    
    logger.info(f"--- LLM Factory: Đang quét tìm key từ 1 đến {SCAN_RANGE}... ---")

    for i in range(1, SCAN_RANGE + 1):
        env_var_name = f"GOOGLE_API_KEY_{i}"
        key = os.getenv(env_var_name)
        
        # Điều kiện: Key không được None (do comment) VÀ không được rỗng (do để trống)
        if key and key.strip():
            keys.append(key.strip())
            # logger.info(f"Loaded {env_var_name}") # Uncomment nếu muốn debug kỹ
            
    if not keys:
        logger.error("CRITICAL: Không tìm thấy bất kỳ GOOGLE_API_KEY_... nào hợp lệ!")
        raise ValueError("Không tìm thấy GOOGLE_API_KEY_... nào trong file .env")
        
    logger.info(f"--- LLM Factory: Đã tải thành công {len(keys)} API keys ---")
    return keys

# --- KHỞI TẠO BỘ XOAY VÒNG KEY ---
API_KEY_POOL: List[str] = _load_api_keys()
# --- THAY ĐỔI LOGIC ---
# Tạo một iterator vĩnh cửu xoay vòng các CHỈ SỐ (0, 1, 2, ...)
_key_cycler: Iterator[int] = itertools.cycle(range(len(API_KEY_POOL)))

# --- SỬA 1: BỎ GẠCH DƯỚI ---
def get_next_api_key() -> str:
    """
    Lấy key tiếp theo trong vòng lặp và GHI LOG.
    """
    # 1. Lấy chỉ số (index) tiếp theo, ví dụ: 0
    key_index = next(_key_cycler)
    
    # 2. Lấy key thật từ Pool, ví dụ: API_KEY_POOL[0]
    key_to_use = API_KEY_POOL[key_index]
    
    # 3. GHI LOG (Đây là điều bạn muốn!)
    # (Sử dụng 'key_index + 1' để log thân thiện hơn, ví dụ: "Key #1")
    logger.info(f"--- LLM FACTORY: Đang sử dụng API Key #{key_index + 1} ---")
    
    # 4. Trả về key
    return key_to_use

# --- CÁC HÀM FACTORY ---

def get_translator_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo một đối tượng LLM Dịch Thuật MỚI với key tiếp theo.
    """
    # --- SỬA 2: BỎ GẠCH DƯỚI ---
    api_key = get_next_api_key()
    return ChatGoogleGenerativeAI(
        model=config.TRANSLATOR_LLM_MODEL,
        google_api_key=api_key,
        temperature=config.TRANSLATOR_LLM_TEMP
    )

def get_extractor_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo một đối tượng LLM Bóc Tách MỚI với key tiếp theo.
    """
    # --- SỬA 3: BỎ GẠCH DƯỚI ---
    api_key = get_next_api_key()
    llm = ChatGoogleGenerativeAI(
        model=config.EXTRACTOR_LLM_MODEL,
        google_api_key=api_key,
        temperature=config.EXTRACTOR_LLM_TEMP
    )
    return llm.with_structured_output(config.ScholarshipSearchFilters)

def get_generator_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo một đối tượng LLM Sinh Câu Trả Lời MỚI với key tiếp theo.
    """
    # --- SỬA 4: BỎ GẠCH DƯỚI ---
    api_key = get_next_api_key()
    llm = ChatGoogleGenerativeAI(
        model=config.GENERATOR_LLM_MODEL,
        google_api_key=api_key,
        temperature=config.GENERATOR_LLM_TEMP
    )
    return llm.with_structured_output(config.ScholarshipAnswer)