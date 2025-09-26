from typing import Optional
from datetime import datetime
import json

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


    def __repr__(self):
        return f"<Applicant: {self.name}, GPA: {self.gpa_range_4}, Degree: {self.degree}, Field: {self.field_of_study}>"
    
    def __str__(self):
            # Helper function to format list attributes
            def format_list(items):
                if not items:
                    return "N/A"
                return "\n".join([f"  - {item}" for item in items])

            # Helper function to format single values, checking for None
            def format_value(value, default="N/A"):
                return value if value is not None else default

            return f"""
            ========================================
            HỒ SƠ ỨNG VIÊN: {format_value(self.name, 'Chưa cập nhật')}
            ========================================

            --- THÔNG TIN CÁ NHÂN ---
            - Email: {format_value(self.email)}
            - Giới tính: {format_value(self.gender)}
            - Ngày sinh: {format_value(self.birth_date)}
            - GPA (hệ 4): {format_value(self.gpa_range_4)}

            --- NGUYỆN VỌNG HỌC BỔNG ---
            - Loại học bổng: {format_value(', '.join(self.desired_scholarship_type or []))}
            - Quốc gia: {format_value(', '.join(self.desired_countries or []))}
            - Mức tài trợ: {format_value(', '.join(self.desired_funding_level or []))}
            - Lĩnh vực mong muốn: {format_value(', '.join(self.desired_field_of_study or []))}

            --- HỒ SƠ HỌC THUẬT & KINH NGHIỆM ---
            - Trình độ: {format_value(self.degree)}
            - Ngành học: {format_value(self.field_of_study)}
            - Chứng chỉ ngoại ngữ:
    {format_list(self.language_certificates)}
            - Chứng chỉ học thuật khác:
    {format_list(self.academic_certificates)}
            - Giải thưởng học thuật:
    {format_list(self.academic_awards)}
            - Công bố khoa học:
    {format_list(self.publications)}
            - Số năm kinh nghiệm: {format_value(self.years_of_experience)}

            --- THÔNG TIN KHÁC ---
            - Ghi chú thêm: {format_value(self.notes)}
            - Các kỹ năng (Tags): {format_value(', '.join(self.tags or []))}
            
            - ĐIỂM ĐẶC BIỆT:
            {format_value(self.special_things)}
            ========================================
            """
    
    def to_json(self):
        """Chuyển đổi các thuộc tính của object thành chuỗi JSON."""
        return json.dumps(
            self.__dict__,
            indent=4,         # Giúp định dạng JSON đẹp hơn
            ensure_ascii=False  # Đảm bảo hiển thị đúng tiếng Việt
        )