# Convert google sheet file to DataFrame and Json format
# For details, see notebooks/test_get_bronze_data.ipynb

from datetime import datetime
import pandas as pd
import os

# Translate column names from Vietnamese to English
mapping = {
    "Tên_học_bổng": "Scholarship_Name",
    "Loại_học_bổng": "Scholarship_Type",
    "Quốc_gia": "Country",
    "Mức_tài_trợ": "Funding_Level",
    "Chi_tiết_tài_trợ": "Funding_Details",
    "Hình_thức_mở": "Application_Mode",
    "Tháng_mở_đơn_(với_thường_niên)": "Application_Month",
    "Ngày_bắt_đầu": "Start_Date",
    "Ngày_kết_thúc": "End_Date",
    "Số_lượng_(nếu_có)": "Quantity",
    "Có_dành_cho_sinh_viên_Việt_Nam_không": "For_Vietnamese",
    "Giới_hạn_đối_tượng": "Eligibility",
    "Giới_hạn_ngành_nghề": "Field_Restriction",
    "Danh_sách_ngành_nghề_(nếu_có)": "Eligible_Fields",
    "Bằng_cấp_yêu_cầu": "Required_Degree",
    "GPA_tối_thiểu": "Min_GPA",
    "Yêu_cầu_về_Xếp_hạng_của_trường_Cử_nhân": "Bachelor_Ranking_Requirement",
    "Yêu_cầu_sự_liên_quan_của_ngành_học_cử_nhân": "Bachelor_Field_Relevance",
    "Yêu_cầu_số_năm_kinh_nghiệm": "Experience_Years",
    "Yêu_cầu_số_giờ_làm_việc_tối_thiểu": "Min_Working_Hours",
    "Yêu_cầu_chứng_chỉ_ngoại_ngữ": "Language_Certificate",
    "Yêu_cầu_chứng_chỉ_Academic": "Academic_Certificate",
    "Yêu_cầu_giải_thưởng,_thành_tích_học_thuật": "Awards_Requirement",
    "Yêu_cầu_publication": "Publication_Requirement",
    "Độ_tuổi": "Age",
    "Giới_tính": "Gender",
    "Hoàn_cảnh_đặc_biệt": "Special_Circumstances",
    "Kế_hoạch_nghề_nghiệp_sau_tốt_nghiệp": "Career_Plan",
    "Yêu_cầu_Khác": "Other_Requirements",
    "Thông_tin_học_bổng": "Scholarship_Info",
    "Hồ_sơ": "Application_Documents",
    "Timeline": "Timeline",
    "URL": "URL",
    "Checked": "Checked"
}

# normalize column names to Capitalized_Words format
def normalize_col(name):
    parts = name.split("_")
    return "_".join([p.capitalize() for p in parts])

category_cols = ['Scholarship_Type', 
                'Country', 
                'Funding_Level', 
                'Application_Mode', 
                'Application_Month', 
                'Quantity',
                'For_Vietnamese', 
                'Field_Restriction', 
                'Required_Degree',
                'Min_Gpa', 
                'Bachelor_Field_Relevance',
                'Language_Certificate',
                'Academic_Certificate',
                "Awards_Requirement",
                "Publication_Requirement",
                "Age",
                "Gender",
                "Other_Requirements",
                "Checked"
]

real_number_cols = [
'Experience_Years', 
'Min_Working_Hours',
]

date_time_cols = [
    'Start_Date',
    'End_Date'
]

def save_bronze_data(url, path="data/1_bronze"):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Preprocessing data Structure
    df = df.dropna(how='all', axis=0)  # Drop rows where all elements are NaN
    df = df.dropna(how='all', axis=1)  # Drop columns where all elements are NaN
    df = df.drop(columns='STT', axis=1)  # Drop 'STT' column if it exists


    # Convert DataFrame
    df = df.rename(columns=mapping)
    df.columns = [normalize_col(c) for c in df.columns]

    for col in category_cols:
        df[col] = df[col].astype('category')

    for col in real_number_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in date_time_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')  

    string_cols = [col for col in df.columns if col not in category_cols + real_number_cols + date_time_cols]
    for col in string_cols:
        df[col] = df[col].astype('string')

    if not os.path.exists(path):
        os.makedirs(path)
    
    # Save as CSV
    df.to_csv(os.path.join(path, "scholarships.csv"), index=False, encoding='utf-8-sig')
    
    # Save as Parquet
    df.to_parquet(os.path.join(path, "scholarships.parquet"), index=False)
    
    # Save as JSON
    df.to_json(
        os.path.join(path, "scholarships.json"),
        orient="records",
        force_ascii=False,
        indent=2,
        date_format="iso"    # --> "2025-09-19T10:00:00.000Z"
    )


def load_bronze_data(path="data/1_bronze", type="csv"):
    if type == "csv":
        return pd.read_csv(os.path.join(path, "scholarships.csv"))
    elif type == "parquet":
        return pd.read_parquet(os.path.join(path, "scholarships.parquet"))
    elif type == "json":
        return pd.read_json(os.path.join(path, "scholarships.json"), orient="records")
    else:
        raise ValueError("Unsupported file type. Use 'csv', 'parquet', or 'json'.")
    
