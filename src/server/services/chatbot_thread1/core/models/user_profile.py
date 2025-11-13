"""
Module định nghĩa User Profile
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserProfile(BaseModel):
    """Model chứa thông tin profile của người dùng"""
    
    # Thông tin cá nhân
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    
    # Thông tin học vấn
    current_degree: Optional[str] = None  # High School, Bachelor, Master
    gpa: Optional[float] = None
    field_of_study: Optional[str] = None
    university: Optional[str] = None
    
    # Thông tin ngôn ngữ
    language_certificates: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    # Ví dụ: [{"type": "IELTS", "score": 7.0}, {"type": "TOEFL", "score": 90}]
    
    # Kinh nghiệm
    work_experience_years: Optional[int] = 0
    
    # Mục tiêu
    target_degree: Optional[str] = None  # Bachelor, Master, PhD
    target_field: Optional[str] = None
    target_countries: Optional[List[str]] = Field(default_factory=list)
    
    # Tài chính
    budget: Optional[str] = None  # "full_scholarship", "partial", "self_funded"
    
    def to_context_string(self) -> str:
        """Chuyển profile thành chuỗi context để đưa vào prompt"""
        parts = []
        
        if self.name:
            parts.append(f"Tên: {self.name}")
        if self.age:
            parts.append(f"Tuổi: {self.age}")
        if self.nationality:
            parts.append(f"Quốc tịch: {self.nationality}")
        if self.current_degree:
            parts.append(f"Bằng cấp hiện tại: {self.current_degree}")
        if self.gpa:
            parts.append(f"GPA: {self.gpa}")
        if self.field_of_study:
            parts.append(f"Ngành học: {self.field_of_study}")
        if self.language_certificates:
            certs = ", ".join([f"{c['type']}: {c['score']}" for c in self.language_certificates])
            parts.append(f"Chứng chỉ ngôn ngữ: {certs}")
        if self.target_degree:
            parts.append(f"Bậc học mục tiêu: {self.target_degree}")
        if self.target_field:
            parts.append(f"Ngành học mục tiêu: {self.target_field}")
        if self.target_countries:
            parts.append(f"Quốc gia mục tiêu: {', '.join(self.target_countries)}")
        
        return "\n".join(parts) if parts else "Không có thông tin profile"
