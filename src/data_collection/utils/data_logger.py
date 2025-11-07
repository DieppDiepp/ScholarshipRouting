# ### \#\#\# `utils/data_logger.py`

#   * **Mục đích:** Thay thế `json_handler.py` cũ.
#   * **Nội dung:**
#       * `def save_to_rag_db(document: Dict[str, str], filepath: str)`: Hàm này nhận `{"url": ..., "content": ...}` và **append** nó vào file `.jsonl` (mỗi kết quả web trên một dòng mới).
#       * `def save_final_report(all_reports: Dict[str, Any], filepath: str)`: Hàm này nhận dictionary chứa *tất cả* các báo cáo học bổng và ghi đè (overwrite) file JSON chính (giống hàm `append_to_json` cũ của bạn).

# data_collection/utils/data_logger.py

import json
import os
from typing import Dict, Any, List
from agent.state import AgentState # MỚI: Import AgentState để type hinting


# ------------------------------------------------------------------------------
# SỬA: Nâng cấp hàm để xử lý một lô (batch) các state
def save_rag_batch(final_states: List[AgentState], filepath: str):
    """
    Append TẤT CẢ tài liệu RAG từ một lô các state vào file .jsonl.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    total_docs_saved = 0
    with open(filepath, 'a', encoding='utf-8') as f:
        # Lặp qua từng kết quả (state) của mỗi học bổng
        for state in final_states:
            scholarship_name = state.get("scholarship_name", "UNKNOWN")
            documents = state.get("context_documents", [])
            
            # Lặp qua từng tài liệu đã thu thập của học bổng đó
            for doc in documents:
                log_entry = {
                    "scholarship_name": scholarship_name, 
                    "url": doc.get("url"),
                    "content": doc.get("content")
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                total_docs_saved += 1
    
    print(f"💾 Đã ghi {total_docs_saved} tài liệu RAG từ {len(final_states)} học bổng vào file.")

# SỬA: Nâng cấp hàm để xử lý một lô (batch)
def save_draft_report_batch(final_states: List[AgentState], filepath: str):
    """
    Cập nhật file JSON báo cáo nháp với một lô các kết quả.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Thêm tất cả các báo cáo từ lô vào data
    for state in final_states:
        name = state.get("scholarship_name")
        report = state.get("final_report")
        if name and report:
            existing_data[name] = report

    # Ghi lại file CHỈ MỘT LẦN
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
    print(f"📊 Đã cập nhật {len(final_states)} báo cáo nháp vào file: {filepath}")

# SỬA: Nâng cấp hàm để xử lý một lô (batch)
def save_structured_report_batch(final_states: List[AgentState], filepath: str):
    """
    Lưu một lô các báo cáo có cấu trúc vào file JSON (dạng list).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
            if not isinstance(all_data, list): all_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = []

    # Tạo một dict để tra cứu tên học bổng đã có
    existing_names = {item.get("Scholarship_Name"): i for i, item in enumerate(all_data)}
    new_reports_added = 0
    reports_updated = 0

    for state in final_states:
        scholarship_data = state.get("structured_report")
        if not scholarship_data:
            continue
            
        scholarship_name = scholarship_data.get("Scholarship_Name")
        
        if scholarship_name in existing_names:
            # Cập nhật
            index_to_update = existing_names[scholarship_name]
            all_data[index_to_update] = scholarship_data
            reports_updated += 1
        else:
            # Thêm mới
            all_data.append(scholarship_data)
            new_reports_added += 1

    # Ghi lại file CHỈ MỘT LẦN
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    
    print(f"🗃️  Đã lưu file cấu trúc: {new_reports_added} học bổng mới, {reports_updated} học bổng cập nhật.")

# --------------------------------------------------------------------------------

def save_to_rag_db(scholarship_name: str, documents: List[Dict[str, Any]], filepath: str):
    """
    Append một list các tài liệu (kết quả từ Tavily) vào file .jsonl cho RAG.
    Mỗi tài liệu là một dict {"url": ..., "content": ...}.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    print(type(documents)) # Debug: Kiểm tra kiểu dữ liệu của documents - nên là list
    print(documents)       # Debug: In ra nội dung của documents để kiểm tra

    with open(filepath, 'a', encoding='utf-8') as f:
        for doc in documents:
            # Đảm bảo chỉ lưu 2 trường quan trọng cho RAG
            log_entry = {
                "scholarship_name": scholarship_name,
                "url": doc.get("url"),
                "content": doc.get("content")
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    print(f"💾 Đã ghi {len(documents)} tài liệu vào RAG DB: {filepath}")

# SỬA: Đổi tên hàm này cho rõ ràng
def save_draft_report(scholarship_name: str, report: Dict[str, Any], filepath: str):
    """
    Lưu báo cáo nháp JSON 10 mục (để debug).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    existing_data[scholarship_name] = report
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
    print(f"📊 Đã cập nhật báo cáo nháp 10-mục cho '{scholarship_name}' tại: {filepath}")

# MỚI: Hàm để lưu Báo Cáo Văn Bản
def save_text_report(scholarship_name: str, report_text: str, filepath: str):
    """
    Lưu báo cáo văn bản toàn diện (dưới dạng JSON {tên: text}).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    
    # Lưu bài văn bản dưới dạng string
    existing_data[scholarship_name] = report_text
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
    print(f" TXT Đã cập nhật báo cáo VĂN BẢN cho '{scholarship_name}' tại: {filepath}")


# SỬA: Đổi tên hàm cho phù hợp
def save_structured_report(scholarship_data: Dict[str, Any], filepath: str):
    """
    Lưu báo cáo có cấu trúc (flat, ENGLISH) vào một file JSON
    chứa một danh sách (list) các học bổng.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
            if not isinstance(all_data, list): all_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = []

    scholarship_name = scholarship_data.get("Scholarship_Name")
    found_index = -1
    if scholarship_name:
        for i, item in enumerate(all_data):
            if item.get("Scholarship_Name") == scholarship_name:
                found_index = i
                break

    if found_index != -1:
        print(f"  -> Updating scholarship '{scholarship_name}' in the structured file.") # Log tiếng Anh
        all_data[found_index] = scholarship_data
    else:
        print(f"  -> Adding new scholarship '{scholarship_name}' to the structured file.") # Log tiếng Anh
        all_data.append(scholarship_data)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"🗃️  Saved structured English report to: {filepath}") # Log tiếng Anh