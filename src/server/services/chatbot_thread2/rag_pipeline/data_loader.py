import json
import pandas as pd
from typing import List, Dict, Any
from .. import config

def load_structured_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Tải file structured_english_reports_master.json (File 4)
    và chuyển nó thành một map (dictionary) để tra cứu nhanh.
    
    Returns:
        Một dictionary với key là "Scholarship_Name" và value là
        toàn bộ metadata của học bổng đó.
    """
    print(f"Loading metadata from: {config.STRUCTURED_REPORTS_PATH}")
    
    # Dùng pandas để đọc JSON list-of-dicts
    df = pd.read_json(config.STRUCTURED_REPORTS_PATH)
    
    # Chuyển đổi một số kiểu dữ liệu có thể gây lỗi khi làm metadata
    # (Ví dụ: NaN, NaT)
    df = df.fillna("Not available") # Thay thế NaN bằng một chuỗi
    
    # Đặt "Scholarship_Name" làm index để tra cứu nhanh
    # và chuyển lại thành dict
    metadata_map = df.set_index("Scholarship_Name").to_dict(orient="index")
    
    print(f"Loaded {len(metadata_map)} metadata records.")
    return metadata_map

def load_text_reports() -> Dict[str, str]:
    """
    Tải file text_reports_master.json (File 3)
    
    Returns:
        Một dictionary với key là "Scholarship_Name" và value là
        nội dung Markdown (văn bản) của học bổng đó.
    """
    print(f"Loading text reports from: {config.TEXT_REPORTS_PATH}")
    
    with open(config.TEXT_REPORTS_PATH, 'r', encoding='utf-8') as f:
        text_reports = json.load(f)
        
    print(f"Loaded {len(text_reports)} text reports.")
    return text_reports

if __name__ == '__main__':
    # Test nhanh xem 2 hàm load có chạy đúng không
    metadata = load_structured_metadata()
    texts = load_text_reports()
    
    # In thử 1 metadata
    print("\n--- Sample Metadata (Turkiye Burslari) ---")
    print(metadata.get("Turkiye Burslari (Turkey Government Scholarship)"))
    
    # In thử 1 đoạn text
    print("\n--- Sample Text (Government of Brunei) ---")
    print(texts.get("Government of Brunei Darussalam Scholarship")[:200] + "...")