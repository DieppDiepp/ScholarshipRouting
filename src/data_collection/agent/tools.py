# ### \#\#\# `agent/tools.py`

#   * **Mục đích:** Quản lý tool Tavily và logic xoay vòng API.
#   * **Nội dung:**
#       * Class `RotatingTavilyTool`:
#           * `__init__(self, api_keys: List[str])`: Lưu danh sách keys và một bộ đếm `self.current_key_index = 0`.
#           * `get_next_key(self)`: Logic xoay vòng API (`index % num_keys`) và trả về key tiếp theo.
#           * `invoke(self, query: str)`:
#             1.  Lấy key tiếp theo bằng `get_next_key()`.
#             2.  Khởi tạo `TavilySearch(tavily_api_key=...)`.
#             3.  Gọi `tool.invoke({"query": query})`.
#             4.  **Quan trọng:** Lấy kết quả (`content` và `url`) và gọi `utils.data_logger.save_to_rag_db(data)` **ngay tại đây**.
#             5.  Tăng `api_call_count` trong state.
#             6.  Trả về kết quả (chỉ `content` và `url`) cho node.

# data_collection/agent/tools.py

from typing import List, Dict, Any
from langchain_tavily import TavilySearch
import config  # <-- THÊM IMPORT CONFIG

class RotatingTavilyTool:
    """
    Một class gói (wrapper) TavilySearch để tự động xoay vòng API keys.
    """
    def __init__(self, api_keys: List[str]):
        if not api_keys:
            raise ValueError("Danh sách API keys không được rỗng.")
        self.api_keys = api_keys
        self.current_key_index = 0
        self.total_keys = len(api_keys)

    def _get_next_key(self) -> str:
        """Lấy key tiếp theo trong danh sách và tăng chỉ số (xoay vòng)."""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % self.total_keys
        return key

    # SỬA: Cập nhật giá trị default cho max_results
    def invoke(self, query: str, max_results: int = config.TAVILY_MAX_RESULTS_DRILLDOWN) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm với key tiếp theo trong vòng xoay.
        Giá trị max_results mặc định giờ lấy từ config.
        """
        api_key = self._get_next_key()
        print(f"    (Sử dụng API Key #{self.current_key_index}...)")
        
        try:
            tool = TavilySearch(
                tavily_api_key=api_key,
                max_results=max_results,  # <--- Sử dụng giá trị max_results được truyền vào
                include_answer=True,
                include_raw_content=True
            )
            
            response_dict = tool.invoke({"query": query})
            return response_dict.get("results", []) 

        except Exception as e:
            print(f"    Lỗi khi gọi API Key #{self.current_key_index}: {e}")
            return []