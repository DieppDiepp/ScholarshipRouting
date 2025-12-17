import os
import itertools
from typing import List, Iterator, Callable, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted
import logging

from .. import config

# Lấy logger
logger = logging.getLogger(__name__)

def _load_api_keys() -> List[str]:
    """
    Tải tất cả các key có dạng GOOGLE_API_KEY_... từ file .env
    CHO PHÉP SỐ THỨ TỰ BỊ ĐỨT QUÃNG.
    """
    keys = []
    # Quét thử từ 1 đến 50 (hoặc 100 nếu bạn có nhiều hơn)
    # Cách này an toàn hơn 'while True' vì nếu thiếu key ở giữa, nó vẫn tìm tiếp key sau.
    scan_range = 50 
    
    logger.info(f"--- LLM Factory: Đang quét tìm key từ 1 đến {scan_range}... ---")

    for i in range(1, scan_range + 1):
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        
        # Chỉ lấy nếu key tồn tại và không phải chuỗi rỗng
        if key and key.strip():
            keys.append(key.strip())
            # (Optional) Log để debug xem nó load được key số mấy
            # logger.info(f"Loaded GOOGLE_API_KEY_{i}") 
            
    if not keys:
        raise ValueError("Không tìm thấy GOOGLE_API_KEY_... nào trong file .env")
        
    logger.info(f"--- LLM Factory: Đã tải thành công TỔNG CỘNG {len(keys)} API keys ---")
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

# --- HELPER FUNCTION: AUTO-SKIP BAD KEYS ---
def _create_llm_with_retry(
    llm_creator: Callable[[str], Any],
    max_attempts: int = None
) -> Any:
    """
    Helper function để tạo LLM với retry logic.
    Tự động skip sang key tiếp theo nếu gặp 429 (quota exceeded).
    
    Args:
        llm_creator: Function nhận api_key và trả về LLM object
        max_attempts: Số lần thử tối đa (mặc định = số key trong pool)
        
    Returns:
        LLM object đã khởi tạo thành công
        
    Raises:
        ResourceExhausted: Nếu tất cả keys đều hết quota
    """
    if max_attempts is None:
        max_attempts = len(API_KEY_POOL)
    
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            api_key = get_next_api_key()
            llm = llm_creator(api_key)
            
            # Test key bằng cách gọi một request nhỏ
            # (Chỉ test khi tạo, không test mỗi lần dùng)
            # Để tiết kiệm, ta bỏ qua test và chỉ handle lỗi khi invoke
            
            return llm
            
        except ResourceExhausted as e:
            last_error = e
            logger.warning(
                f"⚠️ API Key #{attempt + 1} hết quota (429 error). "
                f"Thử key tiếp theo... ({attempt + 1}/{max_attempts})"
            )
            continue
        except Exception as e:
            # Các lỗi khác không phải quota → không retry
            logger.error(f"❌ Lỗi không mong muốn khi tạo LLM: {e}")
            raise
    
    # Nếu đã thử hết tất cả keys
    logger.error(f"❌ TẤT CẢ {max_attempts} API keys đều hết quota!")
    raise ResourceExhausted(
        f"All {max_attempts} API keys exceeded quota. Please check your billing or wait for quota reset."
    ) from last_error

def invoke_with_retry(chain: Any, input_data: dict, max_attempts: int = None) -> Any:
    """
    Helper function để invoke LLM chain với retry logic.
    Tự động tạo LLM mới với key khác nếu gặp 429.
    
    Args:
        chain: LangChain chain hoặc runnable (prompt | llm)
        input_data: Input dict để truyền vào chain.invoke()
        max_attempts: Số lần thử tối đa
        
    Returns:
        Kết quả từ chain.invoke()
    """
    if max_attempts is None:
        max_attempts = len(API_KEY_POOL)
    
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            return chain.invoke(input_data)
            
        except ResourceExhausted as e:
            last_error = e
            logger.warning(
                f"⚠️ API Key hết quota khi invoke (429 error). "
                f"Thử key tiếp theo... (Attempt {attempt + 1}/{max_attempts})"
            )
            
            # TẠO CHAIN MỚI với key mới
            # (Cách này cần chain được tạo lại, tạm thời raise để xử lý ở caller)
            if attempt < max_attempts - 1:
                continue
            else:
                raise
                
        except Exception as e:
            # Các lỗi khác không retry
            logger.error(f"❌ Lỗi không mong muốn khi invoke: {e}")
            raise
    
    # Nếu đã thử hết
    logger.error(f"❌ TẤT CẢ {max_attempts} attempts đều thất bại!")
    raise ResourceExhausted(
        f"All {max_attempts} attempts failed with quota errors."
    ) from last_error

# --- CÁC HÀM FACTORY (CẬP NHẬT) ---

def get_translator_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo một đối tượng LLM Dịch Thuật MỚI với key tiếp theo.
    Tự động retry nếu gặp key hết quota.
    """
    def creator(api_key: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=config.TRANSLATOR_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.TRANSLATOR_LLM_TEMP
        )
    return _create_llm_with_retry(creator)

def get_extractor_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo một đối tượng LLM Bóc Tách MỚI với key tiếp theo.
    Tự động retry nếu gặp key hết quota.
    """
    def creator(api_key: str) -> ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(
            model=config.EXTRACTOR_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.EXTRACTOR_LLM_TEMP
        )
        return llm.with_structured_output(config.ScholarshipSearchFilters)
    return _create_llm_with_retry(creator)

def get_generator_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo một đối tượng LLM Sinh Câu Trả Lời MỚI với key tiếp theo.
    Tự động retry nếu gặp key hết quota.
    """
    def creator(api_key: str) -> ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(
            model=config.GENERATOR_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.GENERATOR_LLM_TEMP
        )
        return llm.with_structured_output(config.ScholarshipAnswer)
    return _create_llm_with_retry(creator)