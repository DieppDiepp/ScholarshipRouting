# ### \#\#\# `utils/data_logger.py`

#   * **Mục đích:** Thay thế `json_handler.py` cũ.
#   * **Nội dung:**
#       * `def save_to_rag_db(document: Dict[str, str], filepath: str)`: Hàm này nhận `{"url": ..., "content": ...}` và **append** nó vào file `.jsonl` (mỗi kết quả web trên một dòng mới).
#       * `def save_final_report(all_reports: Dict[str, Any], filepath: str)`: Hàm này nhận dictionary chứa *tất cả* các báo cáo học bổng và ghi đè (overwrite) file JSON chính (giống hàm `append_to_json` cũ của bạn).

# data_collection/utils/data_logger.py

import json
import os
from typing import Dict, Any, List

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

def save_final_report(scholarship_name: str, report: Dict[str, Any], filepath: str):
    """
    Cập nhật file JSON báo cáo cuối cùng với kết quả của một học bổng.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Cập nhật báo cáo cho học bổng cụ thể
    existing_data[scholarship_name] = report

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
    
    print(f"📊 Đã cập nhật báo cáo cuối cùng cho '{scholarship_name}' tại: {filepath}")


# SỬA: Đổi tên hàm cho phù hợp
def save_structured_english_report(scholarship_data: Dict[str, Any], filepath: str):
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