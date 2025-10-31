# data_collection/agent/state.py
# AgentState bản chất là một "cấu trúc dữ liệu" (schema), nó nên tồn tại độc lập.


# data_collection/agent/state.py

from typing import TypedDict, List, Dict, Any, Set

class AgentState(TypedDict):
    """
    Đại diện cho "bộ nhớ" của agent.
    """
    scholarship_name: str
    
    # --- Thông tin cho RAG & Context ---
    context_documents: List[Dict]
    visited_urls: Set[str]
    
    # --- Thông tin điều khiển luồng (control flow) ---
    api_call_count: int
    current_loop: int
    
    # "Trí nhớ dài hạn" - Các truy vấn đã thất bại
    failed_queries: Set[str] 
    
    # MỚI: "Trí nhớ ngắn hạn" - Các truy vấn VỪA MỚI chạy trong vòng này
    queries_just_ran: List[str]
    
    # --- Thông tin cho các node sau ---
    missing_information: List[str]
    final_report: Dict

    # MỚI: Báo cáo "phẳng" (flat) đã được trích xuất và dịch
    # flat_vietnamese_report: Dict[str, Any]
    structured_report: Dict