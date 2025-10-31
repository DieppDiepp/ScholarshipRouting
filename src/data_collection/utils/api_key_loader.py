# ### \#\#\# `utils/api_key_loader.py`

#   * **Mục đích:** Y hệt như file bạn đã có.
#   * **Nội dung:** Hàm `load_tavily_api_keys()` để đọc `TAVILY_API_KEY_1`, `_2`, `_3`... từ `.env`.

# data_collection/utils/api_key_loader.py

import os
from typing import List

def load_tavily_api_keys() -> List[str]:
    """
    Quét các biến môi trường và tải tất cả các API key của Tavily
    có tên theo định dạng TAVILY_API_KEY_<số>.
    """
    api_keys = []
    i = 1
    while True:
        key = os.environ.get(f"TAVILY_API_KEY_{i}")
        if key:
            api_keys.append(key)
            i += 1
        else:
            break
            
    if not api_keys:
        raise ValueError("Không tìm thấy API key nào của Tavily. Vui lòng đặt tên chúng là TAVILY_API_KEY_1, ...")
        
    print(f"🔑 Đã tải thành công {len(api_keys)} API keys của Tavily.")
    return api_keys

# --- HÀM MỚI ---
def load_google_api_keys() -> List[str]:
    """
    Quét các biến môi trường và tải tất cả các API key của Google
    có tên theo định dạng GOOGLE_API_KEY_<số>.
    """
    api_keys = []
    i = 1
    while True:
        key = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if key:
            api_keys.append(key)
            i += 1
        else:
            break
            
    if not api_keys:
        raise ValueError("Không tìm thấy API key nào của Google. Vui lòng đặt tên chúng là GOOGLE_API_KEY_1, ...")
        
    print(f"🔑 Đã tải thành công {len(api_keys)} API keys của Google.")
    return api_keys