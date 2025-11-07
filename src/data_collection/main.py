# `main.py`

#   * **Mục đích:** File thực thi chính của bạn.
#   * **Nội dung:**
#     1.  Tải các biến môi trường (`load_dotenv()`).
#     2.  Tải danh sách API keys từ `utils.api_key_loader.load_tavily_api_keys()`.
#     3.  Tải danh sách các học bổng cần tìm (ví dụ: `["Chevening", "Fulbright"]`).
#     4.  Tải các hằng số từ `config.py`.
#     5.  Khởi tạo `LangGraphSearchAgent` (được định nghĩa trong `agent/graph.py`), truyền danh sách API keys vào `__init__`.
#     6.  Chạy một vòng lặp `for` qua từng học bổng, gọi `agent.invoke()` cho mỗi học bổng.
#     7.  Hàm `invoke` của agent sẽ tự động chạy toàn bộ quy trình lặp (research loop) và lưu dữ liệu.

# data_collection/main.py

import os
import argparse # MỚI: Thêm thư viện để đọc tham số
import pandas as pd
from dotenv import load_dotenv
import json 

# --- 1. XỬ LÝ THAM SỐ ĐẦU VÀO (ARGPARSE) ---
# Phải thực hiện việc này TRƯỚC TIÊN
parser = argparse.ArgumentParser(description="Chạy pipeline thu thập thông tin học bổng.")
parser.add_argument(
    "--level", 
    type=str, 
    choices=["master", "bachelor", "phd"], 
    default="master",
    help="Cấp độ học bổng cần xử lý (master, bachelor, or phd)."
)
args = parser.parse_args()

# --- 2. ĐẶT BIẾN MÔI TRƯỜNG ---
# Đây là bước quan trọng nhất. 
# Đặt biến môi trường TRƯỚC KHI import config.
os.environ["SCHOLARSHIP_LEVEL"] = args.level

# --- 3. IMPORT CÁC MODULE (SAU KHI ĐÃ ĐẶT ENV) ---
# Giờ đây, khi các file này được import, chúng sẽ đọc file config.py 
# và tự động lấy đúng đường dẫn dựa trên biến "SCHOLARSHIP_LEVEL"
from utils.api_key_loader import load_tavily_api_keys, load_google_api_keys
from agent.tools import RotatingTavilyTool
from agent.graph import LangGraphSearchAgent
import config # <--- config bây giờ đã được "cấu hình động"
# SỬA: Import hàm lưu trữ đã đổi tên
from utils.data_logger import (
    save_draft_report, 
    save_text_report, 
    save_structured_report
)

# --- CÀI ĐẶT BAN ĐẦU (Giữ nguyên) ---
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

def main():
    print(f"--- STARTING PIPELINE FOR LEVEL: {args.level.upper()} ---")
    
    try:
        tavily_api_keys = load_tavily_api_keys()
        google_api_keys = load_google_api_keys()
    except Exception as e:
        print(f"Error loading API keys: {e}")
        return

    tavily_tool = RotatingTavilyTool(api_keys=tavily_api_keys)
    agent = LangGraphSearchAgent(
        tool=tavily_tool,
        google_api_keys=google_api_keys
    )

    try:
        print(f"Reading CSV file: {config.SCHOLARSHIP_DATA_PATH}")
        df = pd.read_csv(config.SCHOLARSHIP_DATA_PATH)
        scholarship_names = df[config.SCHOLARSHIP_NAME_COLUMN].dropna().unique().tolist()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
        
    test_names = scholarship_names[6:12] # Test with 1 scholarship
    # test_names = scholarship_names # Run all
    print(f"\nWill process {len(test_names)} scholarships.")

    for name in test_names:
        print(f"\n=============================================")
        print(f"🚀 Starting processing for: {name}")

        try:
            final_state = agent.invoke(name)
            print(f"\n--- Processing complete for: {name} ---")

            # SỬA: Cập nhật 3 hàm lưu trữ
            
            # 1. Lưu file báo cáo nháp 10 mục (để debug)
            if final_state.get("final_report"):
                save_draft_report(name, final_state["final_report"], config.DRAFT_REPORTS_PATH)

            # 2. LƯU BÁO CÁO VĂN BẢN MỚI
            if final_state.get("synthesis_report_text"):
                save_text_report(name, final_state["synthesis_report_text"], config.FINAL_TEXT_REPORTS_PATH)

            # 3. Lưu file báo cáo CẤU TRÚC (flat, english)
            if final_state.get("structured_report"):
                save_structured_report(
                    final_state["structured_report"],
                    config.STRUCTURED_ENGLISH_REPORTS_PATH
                )
            
            print(f"  - Total API calls: {final_state['api_call_count']}")
            print(f"  - Total loops: {final_state['current_loop']}")
            print(f"  - Total documents collected: {len(final_state['context_documents'])}")

        except Exception as e:
            print(f"!!!!!! CRITICAL ERROR PROCESSING '{name}': {e} !!!!!!")
            print("Continuing with the next scholarship...")
            continue 

    print("\n=============================================")
    print("--- ENTIRE PIPELINE COMPLETE ---")
    print(f"Check RAG DB: {config.RAG_DATABASE_PATH}")
    print(f"Check Draft Reports (JSON 10-muc): {config.DRAFT_REPORTS_PATH}")
    print(f"Check Text Reports (Markdown): {config.FINAL_TEXT_REPORTS_PATH}")
    print(f"Check Structured Reports (Flat JSON): {config.STRUCTURED_ENGLISH_REPORTS_PATH}")

if __name__ == "__main__":
    main()