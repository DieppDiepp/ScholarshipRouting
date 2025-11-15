"""
API Key Manager - Quản lý và xoay vòng API keys cho Gemini và Tavily
"""
import os
import itertools
import logging
from typing import List, Iterator

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Quản lý và xoay vòng API keys"""
    
    def __init__(self):
        """Khởi tạo API Key Manager"""
        # Load Gemini API keys
        self.gemini_keys = self._load_keys("GOOGLE_API_KEY")
        self.gemini_cycler = itertools.cycle(range(len(self.gemini_keys)))
        
        # Load Tavily API keys
        self.tavily_keys = self._load_keys("TAVILY_API_KEY")
        self.tavily_cycler = itertools.cycle(range(len(self.tavily_keys)))
        
        logger.info(f"✅ API Key Manager initialized: {len(self.gemini_keys)} Gemini keys, {len(self.tavily_keys)} Tavily keys")
    
    def _load_keys(self, prefix: str) -> List[str]:
        """
        Load tất cả API keys có dạng PREFIX_1, PREFIX_2, ...
        
        Args:
            prefix: Prefix của key (GOOGLE_API_KEY hoặc TAVILY_API_KEY)
            
        Returns:
            List các API keys
        """
        keys = []
        i = 1
        while True:
            key = os.getenv(f"{prefix}_{i}")
            if key:
                keys.append(key)
                i += 1
            else:
                break
        
        # Fallback: Nếu không có key dạng PREFIX_1, thử PREFIX (single key)
        if not keys:
            single_key = os.getenv(prefix)
            if single_key:
                keys.append(single_key)
                logger.warning(f"⚠️ Chỉ tìm thấy 1 {prefix}. Khuyến nghị sử dụng {prefix}_1, {prefix}_2, ...")
        
        if not keys:
            raise ValueError(f"Không tìm thấy {prefix} nào trong file .env")
        
        logger.info(f"🔑 Đã tải {len(keys)} {prefix} keys")
        return keys
    
    def get_next_gemini_key(self) -> str:
        """
        Lấy Gemini API key tiếp theo trong vòng xoay
        
        Returns:
            Gemini API key
        """
        key_index = next(self.gemini_cycler)
        key = self.gemini_keys[key_index]
        logger.debug(f"🔄 Sử dụng Gemini API Key #{key_index + 1}/{len(self.gemini_keys)}")
        return key
    
    def get_next_tavily_key(self) -> str:
        """
        Lấy Tavily API key tiếp theo trong vòng xoay
        
        Returns:
            Tavily API key
        """
        key_index = next(self.tavily_cycler)
        key = self.tavily_keys[key_index]
        logger.debug(f"🔄 Sử dụng Tavily API Key #{key_index + 1}/{len(self.tavily_keys)}")
        return key
    
    def get_gemini_key_count(self) -> int:
        """Số lượng Gemini API keys"""
        return len(self.gemini_keys)
    
    def get_tavily_key_count(self) -> int:
        """Số lượng Tavily API keys"""
        return len(self.tavily_keys)


# Global instance
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """
    Lấy global instance của APIKeyManager (Singleton pattern)
    
    Returns:
        APIKeyManager instance
    """
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def get_next_gemini_key() -> str:
    """
    Shortcut: Lấy Gemini API key tiếp theo
    
    Returns:
        Gemini API key
    """
    return get_api_key_manager().get_next_gemini_key()


def get_next_tavily_key() -> str:
    """
    Shortcut: Lấy Tavily API key tiếp theo
    
    Returns:
        Tavily API key
    """
    return get_api_key_manager().get_next_tavily_key()
