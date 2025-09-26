from main_class.file_Applicant import Applicant
from main_class.file_Scholarship import Scholarship
from main_class.file_MasterScholarship import MasterScholarship
from main_class.file_PhDScholarship import PhDScholarship
from main_class.file_ExchangeProgram import ExchangeProgram

import os
cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)

example_applicant_dict = {
    # Data từ đơn đăng ký trên web

    ## Thông tin cá nhân - khi ĐK tài khoản
    "Name": "Lương Đắc Nguyên",
    "Gender": "Nam",
    "Email": "nguyenPROFESTIONAL@example.com",
    "Birth_Date": "2005-09-30",
    "GPA_Range_4": "3.98",

    ## Nguyện vọng về học bổng - Đây là khi lần đầu vô trang tìm kiếm gợi ý học bổng.
    "Desired_Scholarship_Type": ["Chính phủ", "Quỹ, tổ chức"],
    "Desired_Countries": ["Hoa Kỳ", "Anh", "Thụy Sĩ"],
    "Desired_Funding_Level": ["Toàn phần"],
    "Desired_Application_Mode": ["Thường niên"],
    "Desired_Application_Month": [6, 7, 8, 9, 10, 11, 12],
    "Desired_Field_of_Study": ["Data Science", "Finance", "Computer Science", "AI Engineering"], # AI Engineering không có trong database

    ## Khác - text box để ứng viên ghi chú thêm
    "Notes": "Tôi có định hướng rõ ràng trở thành một Kỹ sư AI, không chỉ tập trung vào mô hình mà còn cả hệ thống hoàn chỉnh. Tôi đặc biệt quan tâm đến việc triển khai, mở rộng và duy trì các hệ thống AI một cách đáng tin cậy. Tôi từng làm youtuber chia sẻ kiến thức về IT",

    # Data trích xuất từ CV
        
    ## Thông tin học thuật
    "Degree": ["Sắp tốt nghiệp"],
    "Field_of_Study": ["Data Science"],
    "Language_Certificates": ["IELTS 7.0"],
    "Academic_Certificates": None,
    "Academic_Awards": [
        "Á quân - Web3 & Al Ideathon 2025 (Cấp Quốc gia)",
        "Giải Ba - Math Model Challenge Hanoi 2024 (Cấp Quốc gia)",
        "Giải Nhất - ISE SPARK OF IDEA FALL 2024 (Cấp Trường)",
        "Học bổng Khuyến khích học tập (3/4 học kỳ)",
        "Học bổng Coherent Vietnam 2025",
        "Sinh viên 5 tốt cấp trường 2024"
    ],
    "Publications": None,

    ## Kinh nghiệm làm việc
    "Years_of_Experience": 0,
    "Total_Working_Hours": 0,
    ## Thông tin khác từ CV
    "Tags": ["Lãnh đạo", "Tình nguyện", "Cam kết chở về", "Hoạt động ngoại khóa", "Cam kết học tập nghiêm túc"],
    "Special_Things": "Sinh viên có GPA cao nhất ngành Khoa học Dữ liệu (9.24) tại Trường Đại học Công nghệ thông tin - ĐHQG TP.HCM. Đạt nhiều giải thưởng cấp quốc gia về ý tưởng công nghệ và mô hình toán học, nổi bật là Á quân cuộc thi Web3 & Al Ideathon 2025 với dự án chatbot nông nghiệp thông minh 'Nông Trí Al'. Có kinh nghiệm thực tiễn trong việc xây dựng hệ thống AI hoàn chỉnh (RAG), tích hợp API, và triển khai mô hình. Năng lực lãnh đạo và giao tiếp được chứng minh qua vai trò Trưởng ban Học thuật CLB, Host của talk show công nghệ với các chuyên gia trong ngành, và đạt danh hiệu 'Lớp trưởng Xuất sắc'. Đã nhận được học bổng doanh nghiệp (Coherent Vietnam 2025) và nhiều chứng chỉ chuyên sâu từ các nền tảng uy tín như Stanford Online và DeepLearning.AI",
}

Dacnguyen = Applicant(**example_applicant_dict)
# json_output = Dacnguyen.to_json()
# print(json_output)