import json
from datetime import datetime
import os

def convert_date_format(date_str):
    """
    Chuyển đổi một chuỗi ngày từ 'DD/MM/YYYY' sang 'YYYY-MM-DD'.
    Nếu chuỗi rỗng hoặc không hợp lệ, trả về chuỗi gốc.
    """
    # Trả về ngay lập tức nếu chuỗi rỗng hoặc None
    if not date_str:
        return ""
    
    try:
        # Phân tích cú pháp ngày từ định dạng cũ
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        # Định dạng lại ngày sang định dạng mới
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        # Nếu có lỗi (ví dụ: ngày đã ở định dạng đúng, 
        # hoặc là một văn bản không hợp lệ), trả về chuỗi gốc
        print(f"Cảnh báo: Không thể chuyển đổi '{date_str}'. Giữ nguyên giá trị.")
        return date_str

# --- MAIN SCRIPT ---

# Đường dẫn đầy đủ đến file JSON của bạn
# Sử dụng r'' (raw string) để xử lý dấu \ trong đường dẫn Windows
file_path = r'D:\Git\ScholarshipRouting\src\data_collection\output\old\structured_english_reports_master.json'

# Các trường ngày cần chuyển đổi
date_fields_to_convert = ['Start_Date', 'End_Date']

print(f"Đang xử lý file: {file_path}")

# --- 1. Đọc file JSON ---
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"LỖI: Không tìm thấy file tại đường dẫn: {file_path}")
    exit()
except json.JSONDecodeError:
    print(f"LỖI: File không phải là định dạng JSON hợp lệ.")
    exit()
except Exception as e:
    print(f"LỖI khi đọc file: {e}")
    exit()

# --- 2. Xử lý dữ liệu ---
print("Bắt đầu chuyển đổi định dạng ngày...")
converted_count = 0
total_items = len(data)

# Đảm bảo dữ liệu là một danh sách (list)
if not isinstance(data, list):
    print(f"LỖI: Dữ liệu JSON không phải là một danh sách (list).")
    exit()

for item in data:
    # Đảm bảo item là một từ điển (dict)
    if not isinstance(item, dict):
        print(f"Cảnh báo: Bỏ qua mục không phải từ điển: {item}")
        continue
        
    for field in date_fields_to_convert:
        if field in item:
            original_date = item[field]
            converted_date = convert_date_format(original_date)
            
            if original_date != converted_date:
                converted_count += 1
            
            item[field] = converted_date

print(f"Đã xử lý {total_items} mục. Đã chuyển đổi {converted_count} trường ngày.")

# --- 3. Ghi đè file gốc với dữ liệu đã cập nhật ---
try:
    with open(file_path, 'w', encoding='utf-8') as f:
        # Ghi lại file JSON với định dạng đẹp (indent=4)
        # ensure_ascii=False để giữ lại các ký tự đặc biệt (nếu có)
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Hoàn thành! File đã được cập nhật và lưu tại: {file_path}")

except Exception as e:
    print(f"LỖI khi ghi file: {e}")