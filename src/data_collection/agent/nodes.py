# ### \#\#\# `agent/nodes.py`

#   * **Mục đích:** Chứa code thực thi cho từng node trong graph.
#   * **Nội dung:**
#       * `def initial_search_node(state: AgentState) -> Dict:`
#           * Lấy `scholarship_name` từ `state`.
#           * Gọi `TavilyTool` (từ `agent.tools`) với **prompt ban đầu** (từ `prompts.initial_search`).
#           * Trả về `{"context_documents": ..., "visited_urls": ...}` để cập nhật state.
#       * `def analyze_and_plan_node(state: AgentState) -> Dict:`
#           * Đây là "bộ não" 🧠.
#           * Lấy `context_documents` (nội dung web thô) từ `state`.
#           * Gọi một LLM (ví dụ: Gemini) với **prompt "Plan & Analyze"** (từ `prompts.plan_and_analyze`).
#           * LLM sẽ đọc nội dung và trả về: 1) Dữ liệu đã tìm thấy, và 2) **Danh sách các truy vấn mới** cho thông tin còn thiếu.
#           * Trả về `{"missing_information": ..., "final_report": ...}` (cập nhật báo cáo với những gì đã tìm thấy).
#       * `def drill_down_search_node(state: AgentState) -> Dict:`
#           * Lấy danh sách `missing_information` (các truy vấn) từ `state`.
#           * Nếu danh sách rỗng, bỏ qua.
#           * Nếu có truy vấn, chạy `RunnableParallel` để tìm kiếm song song các truy vấn này.
#           * Trả về `{"context_documents": ...}` (nội dung mới tìm được) để *thêm* vào state.
#       * `def final_synthesis_node(state: AgentState) -> Dict:`
#           * Lấy *toàn bộ* `context_documents` từ state.
#           * Gọi LLM với **prompt "Synthesis"** (từ `prompts.synthesis`) để tạo báo cáo cuối cùng.
#           * Trả về `{"final_report": ...}`.

# data_collection/agent/nodes.py

import os
import json
from typing import Dict, Any, List
# SỬA: Import LLM class để dùng làm type hint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from agent.state import AgentState 
from agent.tools import RotatingTavilyTool
from prompts.initial_search import INITIAL_SEARCH_PROMPT
from prompts.plan_and_analyze import analyze_prompt
from prompts.synthesis import synthesis_prompt 
from prompts.structuring import structuring_prompt
# from utils.data_logger import save_to_rag_db
import config

# --- Node 1: Tìm Kiếm Ban Đầu (Cập nhật) ---
def initial_search_node(state: AgentState, tool: RotatingTavilyTool) -> Dict[str, Any]:
    print(f"\n--- Node: Initial Search (Loop {state['current_loop']}) ---")
    scholarship_name = state["scholarship_name"]
    
    query = INITIAL_SEARCH_PROMPT.format(scholarship_name=scholarship_name)
    print(f"  Đang tìm kiếm: '{query}'")
    
    # SỬA: Lấy max_results từ config
    results = tool.invoke(query, max_results=config.TAVILY_MAX_RESULTS_INITIAL)
    
    valid_results = [res for res in results if res.get("content")]
    print(f"  -> Tìm thấy {len(valid_results)} kết quả hợp lệ.")
    # save_to_rag_db(scholarship_name, valid_results, config.RAG_DATABASE_PATH)
    new_urls = {res.get("url") for res in valid_results}
    
    return {
        # SỬA: valid_results giờ là context_documents ban đầu
        "context_documents": valid_results, 
        "visited_urls": new_urls,
        "api_call_count": state["api_call_count"] + 1,
        "current_loop": state["current_loop"] + 1,
        "failed_queries": set(),
        "queries_just_ran": [query] 
    }

# --- Node 2: Phân Tích & Lập Kế Hoạch (Cập nhật) ---
def analyze_and_plan_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    print(f"\n--- Node: Analyze & Plan (Loop {state['current_loop']}) ---")
    scholarship_name = state["scholarship_name"]
    
    context_str = "\n\n---\n\n".join(
        [f"URL: {doc['url']}\nCONTENT: {doc['content']}" for doc in state["context_documents"]]
    )
    failed_queries_str = "\n".join(state["failed_queries"])
    
    # # SỬA: Sử dụng biến từ file config
    # llm = ChatGoogleGenerativeAI(
    #     model=config.NON_CREATIVE_LLM_MODEL,
    #     temperature=config.NON_CREATIVE_LLM_TEMP,
    #     google_api_key=os.environ.get("GOOGLE_API_KEY")
    # )
    
    analysis_chain = analyze_prompt | llm | JsonOutputParser()
    print("  Đang gọi LLM để phân tích và lập kế hoạch...")
    
    try:
        response = analysis_chain.invoke({
            "scholarship_name": scholarship_name,
            "context": context_str,
            "failed_queries": failed_queries_str
        })
        
        print("  -> LLM phân tích hoàn tất.")
        
        queries_we_just_ran = state.get("queries_just_ran", [])
        current_failed_queries = state.get("failed_queries", set())
        llm_missing_queries = response.get("missing_queries", [])
        truly_missing_queries = []
        
        for q in llm_missing_queries:
            if q in queries_we_just_ran:
                print(f"    -> Phát hiện truy vấn thất bại (lặp lại): '{q}'")
                current_failed_queries.add(q) 
            elif q not in current_failed_queries:
                truly_missing_queries.append(q)
                
        print(f"  -> Truy vấn LLM đề xuất: {len(llm_missing_queries)}.")
        print(f"  -> Truy vấn THỰC SỰ còn thiếu (sau khi lọc): {len(truly_missing_queries)}.")
        
        return {
            "final_report": response.get("report_data"),
            "missing_information": truly_missing_queries,
            "failed_queries": current_failed_queries,
            "queries_just_ran": []
        }
    except Exception as e:
        print(f"  Lỗi khi gọi LLM hoặc parse JSON: {e}")
        return {"missing_information": [], "queries_just_ran": []}

# --- Node 3: Tìm Kiếm Chuyên Sâu (Cập nhật) ---
def drill_down_search_node(state: AgentState, tool: RotatingTavilyTool) -> Dict[str, Any]:
    print(f"\n--- Node: Drill-Down Search (Loop {state['current_loop']}) ---")
    scholarship_name = state["scholarship_name"]
    queries = state["missing_information"]
    
    current_docs = state["context_documents"]
    current_urls = state["visited_urls"]
    
    new_docs = []
    queries_to_run = queries[:config.DRILL_DOWN_QUERY_COUNT] 
    print(f"  Sẽ thực thi {len(queries_to_run)}/{len(queries)} truy vấn còn thiếu.")
    
    api_calls_made = 0
    for query in queries_to_run:
        if state["api_call_count"] + api_calls_made >= config.MAX_API_CALLS_PER_SCHOLARSHIP:
            print("  -> Đã đạt giới hạn API call, dừng tìm kiếm chuyên sâu.")
            break
            
        print(f"  Đang tìm kiếm: '{query}'")
        
        # SỬA: Lấy max_results từ config
        results = tool.invoke(query, max_results=config.TAVILY_MAX_RESULTS_DRILLDOWN)
        
        api_calls_made += 1
        
        for res in results:
            if res.get("url") not in current_urls and res.get("content"):
                new_docs.append(res)
                current_urls.add(res.get("url"))
    
    print(f"  -> Tìm thấy {len(new_docs)} tài liệu mới.")
    # if new_docs:
    #     save_to_rag_db(scholarship_name, new_docs, config.RAG_DATABASE_PATH)
    
    return {
        # SỬA: Nối new_docs vào context_documents
        "context_documents": current_docs + new_docs, 
        "visited_urls": current_urls,
        # ... (các trường khác giữ nguyên) ...
        "missing_information": queries[len(queries_to_run):],
        "api_call_count": state["api_call_count"] + api_calls_made,
        "current_loop": state["current_loop"] + 1,
        "queries_just_ran": queries_to_run
    }

# --- Node 4: Tổng Hợp Cuối Cùng (Cập nhật) ---
def final_synthesis_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    print(f"\n--- Node: Final Synthesis (Creating Text Report) ---")
    
    context_str = "\n\n---\n\n".join(
        [f"URL: {doc['url']}\nCONTENT: {doc['content']}" for doc in state["context_documents"]]
    )
    # Lấy bản nháp JSON cuối cùng từ vòng lặp
    draft_report_str = json.dumps(state["final_report"], indent=2, ensure_ascii=False)
    
    # SỬA: Dùng StrOutputParser() vì chúng ta muốn một BÀI BÁO CÁO (text)
    synthesis_chain = synthesis_prompt | llm | StrOutputParser() 
    
    print("  Đang gọi LLM để viết báo cáo văn bản toàn diện...")
    
    try:
        # Đây là một chuỗi (string)
        report_text = synthesis_chain.invoke({
            "scholarship_name": state["scholarship_name"],
            "context": context_str,
            "draft_report": draft_report_str
        })
        print("  -> Viết báo cáo văn bản hoàn tất.")
        # SỬA: Trả về text report vào trường mới
        return {"synthesis_report_text": report_text} 
    except Exception as e:
        print(f"  Lỗi khi tổng hợp báo cáo văn bản: {e}")
        return {"synthesis_report_text": "Error during synthesis."}
    
    
# --- Node 5: Cấu Trúc (Cập nhật) ---
def structure_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    print(f"\n--- Node: Structure Report (from Text Report ONLY) ---") # Cập nhật log

    # SỬA: Chỉ lấy report text
    synthesis_report = state["synthesis_report_text"]
    
    # SỬA: Xóa context_str
    # context_str = "\n\n---\n\n".join(...)

    structuring_chain = structuring_prompt | llm | JsonOutputParser()

    print("  Đang gọi LLM để trích xuất JSON phẳng cuối cùng...")

    try:
        # SỬA: Chỉ truyền 'synthesis_report' vào chain
        structured_report = structuring_chain.invoke({
            "synthesis_report": synthesis_report
        })

        # Logic còn lại giữ nguyên
        structured_report["Scholarship_Name"] = state["scholarship_name"]
        print("  -> Trích xuất JSON phẳng hoàn tất.")
        return {"structured_report": structured_report}

    except Exception as e:
        print(f"  Lỗi khi cấu trúc báo cáo: {e}")
        return {"structured_report": {}}