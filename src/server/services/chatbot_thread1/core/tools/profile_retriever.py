"""
Tool 4: Profile Retriever - Tải và quản lý Profile của người dùng
"""
from typing import Optional, Dict, Any
from core.models.user_profile import UserProfile
import json

class ProfileRetrieverTool:
    """Tool quản lý profile của người dùng"""
    
    def __init__(self):
        """Khởi tạo Profile Retriever Tool"""
        self.current_profile: Optional[UserProfile] = None
    
    def load_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Tải profile từ dictionary
        
        Args:
            profile_data: Dict chứa thông tin profile
            
        Returns:
            UserProfile object
        """
        try:
            self.current_profile = UserProfile(**profile_data)
            print("✓ Đã tải profile thành công")
            return self.current_profile
        except Exception as e:
            print(f"✗ Lỗi khi tải profile: {e}")
            return None
    
    def load_profile_from_json(self, json_path: str) -> UserProfile:
        """
        Tải profile từ file JSON
        
        Args:
            json_path: Đường dẫn đến file JSON chứa profile
            
        Returns:
            UserProfile object
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            return self.load_profile(profile_data)
        except FileNotFoundError:
            print(f"✗ Không tìm thấy file profile: {json_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"✗ Lỗi đọc file JSON: {e}")
            return None
    
    def get_profile(self) -> Optional[UserProfile]:
        """
        Lấy profile hiện tại
        
        Returns:
            UserProfile object hoặc None nếu chưa load
        """
        return self.current_profile
    
    def update_profile(self, updates: Dict[str, Any]) -> UserProfile:
        """
        Cập nhật profile hiện tại
        
        Args:
            updates: Dict chứa các field cần cập nhật
            
        Returns:
            UserProfile đã được cập nhật
        """
        if self.current_profile is None:
            print("⚠ Chưa có profile, tạo profile mới")
            return self.load_profile(updates)
        
        # Cập nhật các field
        for key, value in updates.items():
            if hasattr(self.current_profile, key):
                setattr(self.current_profile, key, value)
        
        print("✓ Đã cập nhật profile")
        return self.current_profile
    
    def clear_profile(self):
        """Xóa profile hiện tại"""
        self.current_profile = None
        print("✓ Đã xóa profile")
    
    def save_profile(self, json_path: str) -> bool:
        """
        Lưu profile hiện tại vào file JSON
        
        Args:
            json_path: Đường dẫn file để lưu
            
        Returns:
            True nếu lưu thành công, False nếu thất bại
        """
        if self.current_profile is None:
            print("✗ Không có profile để lưu")
            return False
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_profile.dict(), f, ensure_ascii=False, indent=2)
            print(f"✓ Đã lưu profile vào {json_path}")
            return True
        except Exception as e:
            print(f"✗ Lỗi khi lưu profile: {e}")
            return False
    
    def check_eligibility(self, scholarship: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm tra xem người dùng có đủ điều kiện cho học bổng không
        
        Args:
            scholarship: Dict chứa thông tin học bổng
            
        Returns:
            Dict chứa kết quả kiểm tra và lý do
        """
        if self.current_profile is None:
            return {
                "eligible": None,
                "reason": "Chưa có thông tin profile"
            }
        
        checks = []
        eligible = True
        
        # Kiểm tra GPA
        min_gpa_str = scholarship.get("Min_Gpa", "")
        if min_gpa_str and self.current_profile.gpa:
            # TODO: Parse GPA requirement phức tạp hơn
            checks.append(f"GPA của bạn: {self.current_profile.gpa}")
        
        # Kiểm tra tuổi
        age_req = scholarship.get("Age", "")
        if age_req and self.current_profile.age:
            checks.append(f"Tuổi của bạn: {self.current_profile.age}")
        
        # Kiểm tra bằng cấp
        required_degree = scholarship.get("Required_Degree", "")
        if required_degree and self.current_profile.current_degree:
            if self.current_profile.current_degree.lower() not in required_degree.lower():
                eligible = False
                checks.append(f"⚠ Bằng cấp yêu cầu: {required_degree}, bạn có: {self.current_profile.current_degree}")
            else:
                checks.append(f"✓ Bằng cấp phù hợp")
        
        # Kiểm tra ngành học
        eligible_fields = scholarship.get("Eligible_Fields", "")
        if eligible_fields and self.current_profile.target_field:
            if self.current_profile.target_field.lower() not in eligible_fields.lower():
                checks.append(f"⚠ Ngành học của bạn ({self.current_profile.target_field}) có thể không nằm trong danh sách")
            else:
                checks.append(f"✓ Ngành học phù hợp")
        
        return {
            "eligible": eligible,
            "checks": checks,
            "reason": "\n".join(checks) if checks else "Không đủ thông tin để kiểm tra"
        }
