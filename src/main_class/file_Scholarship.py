from datetime import datetime
from typing import Optional, List

class Scholarship:
    """
    Lớp cơ sở đại diện cho một chương trình học bổng.
    Chứa các thông tin và yêu cầu đã được điều chỉnh theo danh sách.
    """
    def __init__(self, **kwargs):
        # Thông tin chung
        self.scholarship_name: Optional[str] = kwargs.get('Scholarship_Name')
        self.scholarship_type: Optional[str] = kwargs.get('Scholarship_Type')
        self.country: Optional[str] = kwargs.get('Country')
        self.url: Optional[str] = kwargs.get('Url')
        self.scholarship_info: Optional[str] = kwargs.get('Scholarship_Info')

        # Thông tin tài trợ
        self.funding_level: Optional[str] = kwargs.get('Funding_Level')
        self.funding_details: Optional[str] = kwargs.get('Funding_Details')

        # Thông tin tuyển sinh
        self.application_mode: Optional[str] = kwargs.get('Application_Mode')
        self.application_month: Optional[int] = kwargs.get('Application_Month')
        self.start_date: Optional[datetime] = kwargs.get('Start_Date')
        self.end_date: Optional[datetime] = kwargs.get('End_Date')
        self.quantity: Optional[str] = kwargs.get('Quantity')
        self.application_documents: Optional[str] = kwargs.get('Application_Documents')
        self.timeline: Optional[str] = kwargs.get('Timeline')

        # Yêu cầu chung về ứng viên
        self.for_vietnamese: Optional[bool] = kwargs.get('For_Vietnamese')
        self.age: Optional[str] = kwargs.get('Age')
        self.gender: Optional[str] = kwargs.get('Gender')
        self.eligibility: Optional[str] = kwargs.get('Eligibility') # Mô tả chung về đối tượng
        self.eligible_applicants: Optional[str] = kwargs.get('Eligible_Applicants') # Danh sách giới hạn đối tượng (nếu có)
        self.special_circumstances: Optional[str] = kwargs.get('Special_Circumstances')
        
        # Yêu cầu về học thuật (chung)
        self.min_gpa: Optional[str] = kwargs.get('Min_Gpa')
        self.awards_requirement: Optional[str] = kwargs.get('Awards_Requirement')
        
        # Yêu cầu về ngành học
        self.field_restriction: Optional[str] = kwargs.get('Field_Restriction')
        self.eligible_fields: Optional[str] = kwargs.get('Eligible_Fields')
        
        # Yêu cầu khác
        self.other_requirements: Optional[str] = kwargs.get('Other_Requirements')

    def __repr__(self):
        return f"<Scholarship: {self.scholarship_name} ({self.country})>"
