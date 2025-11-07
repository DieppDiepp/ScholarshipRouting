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

# SỬA: Đổi tên. Đây là file JSON 10 mục (để debug)
DRAFT_REPORTS_PATH = os.path.join(OUTPUT_DIR, f"scholarship_reports_{LEVEL}.json")

# MỚI: Thêm đường dẫn cho file báo cáo VĂN BẢN (Text Report)
# Chúng ta vẫn lưu nó dưới dạng JSON {tên_hb: "toàn bộ bài văn..."}
FINAL_TEXT_REPORTS_PATH = os.path.join(OUTPUT_DIR, f"text_reports_{LEVEL}.json")

# Đường dẫn cho file JSON phẳng cuối cùng (giữ nguyên)
STRUCTURED_ENGLISH_REPORTS_PATH = os.path.join(OUTPUT_DIR, f"structured_english_reports_{LEVEL}.json")

# --- 3. CẤU HÌNH AGENT (Giữ nguyên) ---
MAX_RESEARCH_LOOPS = 5
MAX_API_CALLS_PER_SCHOLARSHIP = 40
DRILL_DOWN_QUERY_COUNT = 5  # <--- HÃY ĐẢM BẢO DÒNG NÀY TỒN TẠI VÀ ĐÚNG TÊN

# --- CẤU HÌNH TAVILY API (MỚI) ---
TAVILY_MAX_RESULTS_INITIAL = 5  # Số kết quả cho lần tìm kiếm đầu tiên
TAVILY_MAX_RESULTS_DRILLDOWN = 3 # Số kết quả cho mỗi truy vấn drill-down

# --- 4. CẤU HÌNH LLM (Giữ nguyên) ---
NON_CREATIVE_LLM_MODEL = "gemini-2.5-flash"
NON_CREATIVE_LLM_TEMP = 0

# --- CẤU HÌNH PIPELINE (MỚI) ---
# Chọn index để chạy (ví dụ: [6:12] như bạn nói)
SCHOLARSHIP_START_INDEX = 0  # Bắt đầu từ học bổng thứ 6
SCHOLARSHIP_END_INDEX = 12   # Dừng ở học bổng thứ 12 (không bao gồm 12)
# Đặt `None` để chạy đến cuối. Ví dụ: (0, None) là chạy tất cả.

# Số lượng học bổng chạy song song (số luồng)
# Cũng chính là kích thước của 1 "lô" (batch)
PARALLEL_WORKERS = 6