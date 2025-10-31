# ### \#\#\# `config.py`

#   * **Mục đích:** Quản lý các hằng số và cấu hình.
#   * **Nội dung:**
#       * `MAX_RESEARCH_LOOPS = 5` (Số vòng lặp tối đa cho mỗi học bổng).
#       * `MAX_API_CALLS_PER_SCHOLARSHIP = 50` (Tổng ngân sách API call).
#       * `RAG_DATABASE_PATH = "output/rag_database.jsonl"` (Lưu ý: `.jsonl` tốt hơn cho RAG vì bạn chỉ cần append dòng mới).
#       * `FINAL_REPORTS_PATH = "output/scholarship_reports.json"`.

# data_collection/config.py

import os

# --- 1. ĐỌC CẤP ĐỘ (LEVEL) TỪ BIẾN MÔI TRƯỜNG ---
# main.py sẽ đặt biến này. Mặc định là 'master' nếu không được đặt.
LEVEL = os.environ.get("SCHOLARSHIP_LEVEL", "master").lower()

print(f"--- 🚀 ĐANG CHẠY HỆ THỐNG CHO CẤP ĐỘ: {LEVEL.upper()} ---")

# --- 2. CẤU HÌNH ĐƯỜNG DẪN ĐỘNG ---

# Lấy thư mục chứa file config.py (.../data_collection)
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
# Lấy thư mục .../src
PROJECT_ROOT = os.path.dirname(CONFIG_DIR)
# Lấy thư mục .../D:\Git\ScholarshipRouting
GRAND_PROJECT_ROOT = os.path.dirname(PROJECT_ROOT) 

# SỬA: Tạo tên file input động
# Ví dụ: "Master_raw.csv", "Bachelor_raw.csv", "PhD_raw.csv"
input_filename = f"{LEVEL.capitalize()}_raw.csv"
SCHOLARSHIP_DATA_PATH = os.path.join(GRAND_PROJECT_ROOT, "data", "raw_data", input_filename)
SCHOLARSHIP_NAME_COLUMN = "Scholarship_Name"

# SỬA: Tạo tên file output động
OUTPUT_DIR = os.path.join(CONFIG_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ví dụ: "rag_database_master.jsonl", "rag_database_bachelor.jsonl", ...
RAG_DATABASE_PATH = os.path.join(OUTPUT_DIR, f"rag_database_{LEVEL}.jsonl")
# Ví dụ: "scholarship_reports_master.json", "scholarship_reports_bachelor.json", ...
FINAL_REPORTS_PATH = os.path.join(OUTPUT_DIR, f"scholarship_reports_{LEVEL}.json")

# SỬA: Đổi tên file output cuối cùng
STRUCTURED_ENGLISH_REPORTS_PATH = os.path.join(OUTPUT_DIR, f"structured_english_reports_{LEVEL}.json")

# --- 3. CẤU HÌNH AGENT (Giữ nguyên) ---
MAX_RESEARCH_LOOPS = 5
MAX_API_CALLS_PER_SCHOLARSHIP = 50
DRILL_DOWN_QUERY_COUNT = 3

# --- 4. CẤU HÌNH LLM (Giữ nguyên) ---
NON_CREATIVE_LLM_MODEL = "gemini-2.5-flash"
NON_CREATIVE_LLM_TEMP = 0.2