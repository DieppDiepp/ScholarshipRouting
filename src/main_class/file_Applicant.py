from typing import Optional
from datetime import datetime

class Applicant:
    def __init__(self, **kwargs): # Tất cả data user đều có thể chỉnh sửa cho đúng với mình (đề phòng có sai sót khi trích xuất CV)

        # Data từ đơn đăng ký trên web

        ## Thông tin cá nhân - khi ĐK tài khoản
        self.name: Optional[str] = kwargs.get('Name')
        self.gender: Optional[str] = kwargs.get('Gender') # 1 số loại học bổng chỉ dành cho nam/nữ
        self.email: Optional[str] = kwargs.get('Email')
        self.birth_date: Optional[datetime] = kwargs.get('Birth_Date')
        self.gpa_range_4: Optional[float] = kwargs.get('GPA_Range_4')

        ## Nguyện vọng về học bổng - Đây là khi lần đầu vô trang tìm kiếm gợi ý học bổng.
        self.desired_scholarship_type: Optional[list] = kwargs.get('Desired_Scholarship_Type')  # chính phủ, tư nhân, ...
        self.desired_countries: Optional[list] = kwargs.get('Desired_Countries') # danh sách các quốc gia mong muốn
        self.desired_funding_level: Optional[list] = kwargs.get('Desired_Funding_Level') # toàn phần, bán phần, cash...
        self.desired_application_mode: Optional[list] = kwargs.get('Desired_Application_Mode') # thường niên, đột xuất, rolling...
        self.desired_application_month: Optional[int] = kwargs.get('Desired_Application_Month') # tháng muốn nộp đơn
        self.desired_field_of_study: Optional[list] = kwargs.get('Desired_Field_of_Study') # ngành học mong muốn

        ## Khác - text box để ứng viên ghi chú thêm
        self.notes: Optional[str] = kwargs.get('Notes') # ứng viên có thể ghi chú thêm gì đó như hoàn cảnh đặc biệt, khó khăn...

        # Data trích xuất từ CV
        
        ## Thông tin học thuật
        self.degree: Optional[str] = kwargs.get('Degree') 
        self.field_of_study: Optional[str] = kwargs.get('Field_of_Study')
        self.language_certificates: Optional[str] = kwargs.get('Language_Certificates') # danh sách chứng chỉ ngoại ngữ
        self.academic_certificates: Optional[str] = kwargs.get('Academic_Certificates') # danh sách chứng chỉ học thuật
        self.academic_awards: Optional[str] = kwargs.get('Academic_Awards') # danh sách giải thưởng học thuật
        self.publications: Optional[str] = kwargs.get('Publications') # danh sách các công bố khoa học

        ## Kinh nghiệm làm việc
        self.years_of_experience: Optional[float] = kwargs.get('Years_of_Experience')
        self.total_working_hours: Optional[float] = kwargs.get('Total_Working_Hours')

        ## Thông tin khác từ CV
        self.tags: Optional[list] = kwargs.get('Tags') # các tag gắn với CV, ví dụ "Nghiên cứu", "Lãnh đạo", "Tình nguyện", "Cam kết chở về"
        self.special_things: Optional[str] = kwargs.get('Special_Things') # Các thứ thật sự đặc biệt, mà có thể giúp ứng viên nổi bật hơn


