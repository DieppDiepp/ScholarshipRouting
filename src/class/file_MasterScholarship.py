from .file_Scholarship import Scholarship
from typing import Optional

class MasterScholarship(Scholarship):
    """
    Đại diện cho học bổng Thạc sĩ.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # SỬA ĐỔI: Tải yêu cầu bằng cấp trực tiếp từ dữ liệu
        self.required_degree: Optional[str] = kwargs.get('Required_Degree')
        
        # Yêu cầu liên quan đến bằng Cử nhân
        self.bachelor_ranking_requirement: Optional[str] = kwargs.get('Bachelor_Ranking_Requirement')
        self.bachelor_field_relevance: Optional[str] = kwargs.get('Bachelor_Field_Relevance')

        # Yêu cầu về kinh nghiệm
        self.experience_years: Optional[float] = kwargs.get('Experience_Years')
        self.min_working_hours: Optional[float] = kwargs.get('Min_Working_Hours')

        # Yêu cầu về chứng chỉ
        self.language_certificate: Optional[str] = kwargs.get('Language_Certificate')
        self.academic_certificate: Optional[str] = kwargs.get('Academic_Certificate')

        # Yêu cầu về nghiên cứu
        self.publication_requirement: Optional[str] = kwargs.get('Publication_Requirement')
        
        # Kế hoạch sau tốt nghiệp
        self.carrer_plan: Optional[str] = kwargs.get('Carrer_Plan')