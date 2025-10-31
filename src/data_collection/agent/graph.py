# ### \#\#\# `agent/graph.py`

#   * **Mục đích:** Trái tim của agent, định nghĩa logic của LangGraph.
#   * **Nội dung:**
#     1.  Import các hàm `node` từ `agent.nodes`.
#     2.  **Định nghĩa `AgentState(TypedDict)`:** Đây là "bộ nhớ" của agent.
#           * `scholarship_name: str`
#           * `api_keys: List[str]` (Danh sách key được truyền vào)
#           * `api_call_count: int` (Bộ đếm số API đã dùng)
#           * `current_loop: int` (Bộ đếm số vòng lặp)
#           * `visited_urls: Set[str]` (Để tránh crawl lại trang đã xem)
#           * `context_documents: List[Dict]` (Danh sách `{"url": ..., "content": ...}`)
#           * `missing_information: List[str]` (Danh sách các truy vấn mới do LLM tạo ra)
#           * `final_report: Dict` (Kết quả cuối cùng)
#     3.  **Class `LangGraphSearchAgent`:**
#           * `__init__(self, all_api_keys)`: Lưu danh sách keys.
#           * `build_graph(self)`:
#               * `graph = StateGraph(AgentState)`
#               * Thêm các nodes: `graph.add_node("initial_search", initial_search_node)`...
#               * Thêm các edges: `graph.set_entry_point("initial_search")`
#               * Thêm **Conditional Edge** (Cạnh điều kiện):
#                   * `graph.add_conditional_edges("drill_down_search", should_continue_looping)`
#                   * Hàm `should_continue_looping` sẽ kiểm tra `state` (số vòng lặp, số api call) để quyết định đi đến node `plan_and_analyze` (lặp lại) hay node `final_synthesis` (kết thúc).
#           * `invoke(self, scholarship_name)`: Gọi `graph.compile().invoke(...)` với `AgentState` ban đầu.

# data_collection/agent/graph.py

from langgraph.graph import StateGraph, END
from functools import partial 
import config 
from typing import List # MỚI: Thêm List

from agent.state import AgentState 
from agent.tools import RotatingTavilyTool
# MỚI: Import LLM class
from langchain_google_genai import ChatGoogleGenerativeAI

# SỬA: Import cả 5 node
from agent.nodes import (
    initial_search_node, 
    analyze_and_plan_node, 
    drill_down_search_node,
    final_synthesis_node,
    structure_node # <--- MỚI
)

# Hàm điều kiện (giữ nguyên, không thay đổi)
def should_continue_looping(state: AgentState) -> str:
    print(f"\n--- Node: Conditional Edge (Kiểm tra điều kiện) ---")
    queries = state["missing_information"]
    loop = state["current_loop"]
    api_calls = state["api_call_count"]
    
    if not queries:
        print("  -> Quyết định: Đã đủ thông tin. Bắt đầu tổng hợp cuối.")
        return "end_loop"
    if loop >= config.MAX_RESEARCH_LOOPS:
        print(f"  -> Quyết định: Đạt giới hạn {config.MAX_RESEARCH_LOOPS} vòng lặp. Bắt đầu tổng hợp cuối.")
        return "end_loop"
    if api_calls >= config.MAX_API_CALLS_PER_SCHOLARSHIP:
        print(f"  -> Quyết định: Đạt giới hạn {config.MAX_API_CALLS_PER_SCHOLARSHIP} API call. Bắt đầu tổng hợp cuối.")
        return "end_loop"
    
    print("  -> Quyết định: Còn thông tin thiếu. TIẾP TỤC LẶP.")
    return "continue_drill_down"

# --- XÂY DỰNG CLASS AGENT (Giữ nguyên) ---
class LangGraphSearchAgent:
    
    # SỬA: Cập nhật hàm __init__
    def __init__(self, tool: RotatingTavilyTool, google_api_keys: List[str]):
        self.tool = tool
        
        # MỚI: Lưu trữ thông tin xoay vòng Google API key
        if not google_api_keys:
            raise ValueError("Danh sách Google API keys không được rỗng.")
        self.google_api_keys = google_api_keys
        self.num_google_keys = len(google_api_keys)
        self.google_key_index = 0 # Bộ đếm
        
        self.app = self.build_graph()

    # MỚI: Thêm hàm helper để lấy LLM với key xoay vòng
    def _get_llm_instance(self) -> ChatGoogleGenerativeAI:
        """
        Lấy một instance LLM với API key tiếp theo trong vòng xoay.
        """
        # 1. Lấy key tiếp theo
        key = self.google_api_keys[self.google_key_index]
        
        # 2. Cập nhật index cho lần gọi sau
        current_index_for_log = self.google_key_index + 1 # (Chỉ để log cho đẹp)
        self.google_key_index = (self.google_key_index + 1) % self.num_google_keys
        
        print(f"    (Sử dụng Google API Key #{current_index_for_log}...)")
        
        # 3. Trả về một instance LLM mới với key đó
        return ChatGoogleGenerativeAI(
            model=config.NON_CREATIVE_LLM_MODEL,
            temperature=config.NON_CREATIVE_LLM_TEMP,
            google_api_key=key
        )

    # --- Các hàm partial để truyền tool/llm vào node ---
    
    def _partial_initial_search(self, state: AgentState):
        # Node này chỉ dùng tool
        return initial_search_node(state, self.tool)
    
    def _partial_drill_down_search(self, state: AgentState):
        # Node này chỉ dùng tool
        return drill_down_search_node(state, self.tool)

    # MỚI: Các hàm partial cho các node dùng LLM
    def _partial_analyze_and_plan(self, state: AgentState):
        # Lấy một LLM mới với key xoay vòng
        llm_instance = self._get_llm_instance()
        # Truyền nó vào node
        return analyze_and_plan_node(state, llm_instance)

    def _partial_final_synthesis(self, state: AgentState):
        llm_instance = self._get_llm_instance()
        return final_synthesis_node(state, llm_instance)

    def _partial_structure_node(self, state: AgentState):
        llm_instance = self._get_llm_instance()
        return structure_node(state, llm_instance)

    # --- XÂY DỰNG ĐỒ THỊ (Cập nhật) ---
    def build_graph(self):
        graph = StateGraph(AgentState) 
        
        # SỬA: Dùng các hàm partial mới
        graph.add_node("initial_search", self._partial_initial_search)
        graph.add_node("drill_down_search", self._partial_drill_down_search)
        
        graph.add_node("analyze_and_plan", self._partial_analyze_and_plan) # <--- SỬA
        graph.add_node("final_synthesis", self._partial_final_synthesis) # <--- SỬA
        graph.add_node("structure", self._partial_structure_node) # <--- SỬA
        
        # (Phần còn lại của graph.add_edge và conditional_edges giữ nguyên)
        graph.set_entry_point("initial_search")
        graph.add_edge("initial_search", "analyze_and_plan")
        graph.add_conditional_edges(
            "analyze_and_plan",
            should_continue_looping,
            {"continue_drill_down": "drill_down_search", "end_loop": "final_synthesis"}
        )
        graph.add_edge("drill_down_search", "analyze_and_plan")
        graph.add_edge("final_synthesis", "structure")
        graph.add_edge("structure", END)
        
        print("Biên dịch Agent Graph (Giai Đoạn 7 - Xoay vòng LLM) thành công.")
        return graph.compile()

# --- PHƯƠNG THỨC INVOKE (Cập nhật) ---
    def invoke(self, scholarship_name: str):
        # SỬA: Thêm synthesis_report_text vào state ban đầu
        initial_state = {
            "scholarship_name": scholarship_name,
            "api_call_count": 0,
            "current_loop": 0,
            "visited_urls": set(),
            "context_documents": [],
            "missing_information": [],
            "final_report": {},       # Báo cáo nháp
            "failed_queries": set(),
            "queries_just_ran": [],
            "synthesis_report_text": "", # <-- MỚI: Báo cáo văn bản
            "structured_report": {}
        }
        final_state = self.app.invoke(initial_state)
        return final_state