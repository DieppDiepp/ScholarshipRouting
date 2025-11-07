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
from typing import List, Dict, Any
# MỚI: Import ThreadPoolExecutor và helper
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
from agent.graph import LangGraphSearchAgent, AgentState
import config # <--- config bây giờ đã được "cấu hình động"
# SỬA: Import hàm lưu trữ đã đổi tên
from utils.data_logger import (
    save_draft_report_batch, 
    save_text_report, # Hàm này vẫn lưu 1-1, chúng ta sẽ gọi nó từ main
    save_structured_report_batch,
    save_rag_batch
)

# --- CÀI ĐẶT BAN ĐẦU (Giữ nguyên) ---
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# --- (HÀM WORKER CHO LUỒNG SONG SONG) ---
def run_single_scholarship(scholarship_name: str, tavily_keys: List[str], google_keys: List[str]) -> AgentState:
    """
    Hàm này được chạy trong một luồng (thread) riêng biệt.
    Nó khởi tạo agent và chạy invoke cho 1 học bổng.
    NÓ KHÔNG GHI FILE.
    """
    print(f"  [Thread] 🚀 Bắt đầu xử lý cho: {scholarship_name}")
    try:
        # Mỗi luồng phải tạo instance riêng để tránh xung đột
        tavily_tool = RotatingTavilyTool(api_keys=tavily_keys)
        agent = LangGraphSearchAgent(
            tool=tavily_tool,
            google_api_keys=google_keys
        )
        
        # Chạy agent
        final_state = agent.invoke(scholarship_name)
        print(f"  [Thread] ✅ Hoàn tất xử lý cho: {scholarship_name}")
        return final_state
    
    except Exception as e:
        print(f"  [Thread] ❌ LỖI khi xử lý '{scholarship_name}': {e}")
        # Trả về một state lỗi để main thread có thể log
        return {
            "scholarship_name": scholarship_name,
            "error": str(e) 
        }

# --- (HÀM HELPER ĐỂ CHIA LÔ) ---
def create_batches(data: list, batch_size: int):
    """Chia một list thành các list nhỏ (lô)."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

# --- (HÀM MAIN MỚI) ---
def main():
    print(f"--- STARTING PIPELINE FOR LEVEL: {args.level.upper()} ---")
    
    try:
        tavily_api_keys = load_tavily_api_keys()
        google_api_keys = load_google_api_keys()
    except Exception as e:
        print(f"Error loading API keys: {e}")
        return

    try:
        print(f"Reading CSV file: {config.SCHOLARSHIP_DATA_PATH}")
        df = pd.read_csv(config.SCHOLARSHIP_DATA_PATH)
        all_scholarship_names = df[config.SCHOLARSHIP_NAME_COLUMN].dropna().unique().tolist()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
        
    # SỬA: Cắt (slice) danh sách dựa trên config
    start = config.SCHOLARSHIP_START_INDEX
    end = config.SCHOLARSHIP_END_INDEX
    scholarships_to_run = all_scholarship_names[start:end]
    
    print(f"\nĐã tìm thấy {len(all_scholarship_names)} học bổng. Sẽ chạy {len(scholarships_to_run)} học bổng (từ index {start} đến {end}).")
    print(f"Sẽ chạy song song với {config.PARALLEL_WORKERS} luồng, kích thước lô {config.PARALLEL_WORKERS}.")

    start_time = time.time()
    
    # Tạo các lô
    batches = list(create_batches(scholarships_to_run, config.PARALLEL_WORKERS))
    
    for i, batch_names in enumerate(batches):
        print(f"\n=============================================")
        print(f"🚀 Bắt đầu xử lý Lô {i+1}/{len(batches)} (gồm {len(batch_names)} học bổng)...")
        
        batch_results: List[AgentState] = []
        
        # Tạo ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=config.PARALLEL_WORKERS) as executor:
            # Gửi các tác vụ vào pool
            futures = {
                executor.submit(
                    run_single_scholarship, 
                    name, 
                    tavily_api_keys, 
                    google_api_keys
                ): name for name in batch_names
            }
            
            # Thu thập kết quả khi chúng hoàn thành
            for future in as_completed(futures):
                result_state = future.result()
                batch_results.append(result_state)

        print(f"\n--- Lô {i+1} hoàn tất. Bắt đầu ghi dữ liệu... ---")
        
        # --- GHI DỮ LIỆU (CHẠY TRÊN MAIN THREAD) ---
        
        # Lọc ra các state thành công
        successful_states = [s for s in batch_results if "error" not in s]
        failed_states = [s for s in batch_results if "error" in s]

        if successful_states:
            # 1. Ghi vào RAG DB (append .jsonl)
            save_rag_batch(successful_states, config.RAG_DATABASE_PATH)
            
            # 2. Ghi báo cáo nháp (debug)
            save_draft_report_batch(successful_states, config.DRAFT_REPORTS_PATH)
            
            # 3. Ghi báo cáo văn bản
            for state in successful_states:
                save_text_report(
                    state["scholarship_name"], 
                    state.get("synthesis_report_text", "Error: No text report generated"), 
                    config.FINAL_TEXT_REPORTS_PATH
                )
            
            # 4. Ghi báo cáo cấu trúc cuối cùng
            save_structured_report_batch(successful_states, config.STRUCTURED_ENGLISH_REPORTS_PATH)
        
        if failed_states:
            print(f"❌ Cảnh báo: {len(failed_states)} học bổng trong lô thất bại:")
            for state in failed_states:
                print(f"  - {state['scholarship_name']}: {state['error']}")

    end_time = time.time()
    print("\n=============================================")
    print(f"--- TOÀN BỘ PIPELINE HOÀN TẤT TRONG {end_time - start_time:.2f} GIÂY ---")
    print(f"Kiểm tra file RAG DB: {config.RAG_DATABASE_PATH}")
    print(f"Kiểm tra file Báo Cáo Nháp: {config.DRAFT_REPORTS_PATH}")
    print(f"Kiểm tra file Báo Cáo Văn Bản: {config.FINAL_TEXT_REPORTS_PATH}")
    print(f"Kiểm tra file Báo Cáo Cấu Trúc: {config.STRUCTURED_ENGLISH_REPORTS_PATH}")

if __name__ == "__main__":
    main()