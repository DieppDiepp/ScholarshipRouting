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
from utils.data_logger import save_final_report, save_structured_english_report

# --- CÀI ĐẶT BAN ĐẦU (Giữ nguyên) ---
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

def main():
    print(f"--- STARTING PIPELINE FOR LEVEL: {args.level.upper()} ---") # Log tiếng Anh
    try:
        # 1. Tải cả hai danh sách keys
        tavily_api_keys = load_tavily_api_keys()
        google_api_keys = load_google_api_keys()

    except Exception as e:
        print(f"Error loading API keys: {e}") # Log tiếng Anh
        return

    tavily_tool = RotatingTavilyTool(api_keys=tavily_api_keys)
    # 3. SỬA: Khởi tạo Agent và truyền cả hai vào
    agent = LangGraphSearchAgent(
        tool=tavily_tool,
        google_api_keys=google_api_keys
    )

    try:
        print(f"Reading CSV file: {config.SCHOLARSHIP_DATA_PATH}") # Log tiếng Anh
        df = pd.read_csv(config.SCHOLARSHIP_DATA_PATH)
        scholarship_names = df[config.SCHOLARSHIP_NAME_COLUMN].dropna().unique().tolist()
    except Exception as e:
        print(f"Error reading CSV file: {e}") # Log tiếng Anh
        return

    test_names = scholarship_names[6:10] # Test with 1 scholarship
    # test_names = scholarship_names # Run all
    print(f"\nWill process {len(test_names)} scholarships.") # Log tiếng Anh

    for name in test_names:
        print(f"\n=============================================")
        print(f"🚀 Starting processing for: {name}") # Log tiếng Anh

        try:
            final_state = agent.invoke(name)
            print(f"\n--- Processing complete for: {name} ---") # Log tiếng Anh

            # Save draft report (for debugging)
            if final_state.get("final_report"):
                save_final_report(name, final_state["final_report"], config.FINAL_REPORTS_PATH)

            # SỬA: Save structured ENGLISH report
            if final_state.get("structured_report"):
                save_structured_english_report( # Gọi hàm đã đổi tên
                    final_state["structured_report"],
                    config.STRUCTURED_ENGLISH_REPORTS_PATH # Dùng đường dẫn đã đổi tên
                )

            print(f"  - Total API calls: {final_state['api_call_count']}") # Log tiếng Anh
            print(f"  - Total loops: {final_state['current_loop']}") # Log tiếng Anh
            print(f"  - Total documents collected: {len(final_state['context_documents'])}") # Log tiếng Anh

        except Exception as e:
            print(f"!!!!!! CRITICAL ERROR PROCESSING '{name}': {e} !!!!!!") # Log tiếng Anh
            print("Continuing with the next scholarship...") # Log tiếng Anh
            continue

    print("\n=============================================")
    print("--- ENTIRE PIPELINE COMPLETE ---") # Log tiếng Anh
    print(f"Check RAG DB: {config.RAG_DATABASE_PATH}") # Log tiếng Anh
    print(f"Check Draft Reports: {config.FINAL_REPORTS_PATH}") # Log tiếng Anh
    print(f"Check Structured English Reports: {config.STRUCTURED_ENGLISH_REPORTS_PATH}") # Log tiếng Anh

if __name__ == "__main__":
    main()