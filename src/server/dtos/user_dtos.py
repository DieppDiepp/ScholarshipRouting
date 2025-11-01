# dtos/user_dtos.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime

# DTO cho Profile của người dùng
class UserProfile(BaseModel):
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    gpa_range_4: Optional[float] = None

    # --- Nguyện vọng về học bổng (đây là các trường chính để tạo filter) ---
    desired_scholarship_type: Optional[List[str]] = None
    desired_countries: Optional[List[str]] = None
    desired_funding_level: Optional[List[str]] = None
    desired_application_mode: Optional[List[str]] = None
    desired_application_month: Optional[int] = None # Sẽ cần chuyển đổi sang định dạng phù hợp
    desired_field_of_study: Optional[List[str]] = None

    # --- Dữ liệu trích xuất từ CV (cũng có thể dùng làm filter) ---
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    language_certificates: Optional[str] = None
    academic_certificates: Optional[str] = None
    academic_awards: Optional[str] = None
    publications: Optional[str] = None

    # --- Kinh nghiệm làm việc ---
    years_of_experience: Optional[float] = None
    total_working_hours: Optional[float] = None

    # --- Thông tin khác ---
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    special_things: Optional[str] = None


# DTOs for tracking scholarship interests (calendar items)
class ScholarshipInterest(BaseModel):
    """A simple scholarship interest item for calendar display.
    
    Only includes essential fields needed for calendar visualization:
    - scholarship_id: unique id of scholarship
    - name: name/title of the scholarship
    - open_date: when applications open
    - close_date: when applications close
    """
    scholarship_id: str
    name: str
    open_date: datetime
    close_date: datetime


# Removed UserInterestsUpdate DTO since we're handling single interest operations