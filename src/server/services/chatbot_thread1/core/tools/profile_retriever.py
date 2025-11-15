"""
Tool 4: Profile Retriever - Tải và quản lý Profile của người dùng
"""
from typing import Optional, Dict, Any
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.core.models.user_profile import UserProfile


class ProfileRetrieverTool:
    """Tool quản lý profile của người dùng"""
    
    def __init__(self):
        """Khởi tạo Profile Retriever Tool"""
        self.current_profile: Optional[UserProfile] = None
    
    def get_profile_string(self) -> str:
        """
        Lấy profile dưới dạng string
        
        Returns:
            String representation của profile
        """
        if self.current_profile is None:
            return "Chưa có thông tin profile."
        return self.current_profile.to_context_string()
    
    def load_profile(self, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """
        Tải profile từ dictionary
        
        Args:
            profile_data: Dict chứa thông tin profile
            
        Returns:
            UserProfile object hoặc None nếu lỗi
        """
        if not profile_data:
            print("⚠ Profile data rỗng")
            return None
            
        try:
            self.current_profile = UserProfile(**profile_data)
            print("✓ Đã tải profile thành công")
            return self.current_profile
        except Exception as e:
            print(f"✗ Lỗi khi tải profile: {e}")
            return None
    
    def load_profile_from_json(self, json_path: str) -> Optional[UserProfile]:
        """
        Tải profile từ file JSON
        
        Args:
            json_path: Đường dẫn đến file JSON chứa profile
            
        Returns:
            UserProfile object hoặc None nếu lỗi
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            return self.load_profile(profile_data)
        except FileNotFoundError:
            print(f"✗ File không tồn tại: {json_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"✗ JSON không hợp lệ: {e}")
            return None
        except Exception as e:
            print(f"✗ Lỗi không xác định: {e}")
            return None
    
    def get_profile(self) -> Optional[UserProfile]:
        """
        Lấy profile hiện tại
        
        Returns:
            UserProfile object hoặc None nếu chưa load
        """
        return self.current_profile
    
    def update_profile(self, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """
        Cập nhật profile hiện tại
        
        Args:
            updates: Dict chứa các field cần cập nhật
            
        Returns:
            UserProfile đã được cập nhật hoặc None
        """
        if not updates:
            print("⚠ Không có dữ liệu để cập nhật")
            return self.current_profile
            
        if self.current_profile is None:
            print("⚠ Chưa có profile, tạo mới")
            return self.load_profile(updates)
        
        # Cập nhật các field hợp lệ
        updated_count = 0
        for key, value in updates.items():
            if hasattr(self.current_profile, key):
                setattr(self.current_profile, key, value)
                updated_count += 1
        
        if updated_count > 0:
            print(f"✓ Đã cập nhật {updated_count} field(s)")
        else:
            print("⚠ Không có field nào được cập nhật")
            
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
        Kiểm tra điều kiện đủ điều kiện cho học bổng
        
        Args:
            scholarship: Dict chứa thông tin học bổng
            
        Returns:
            Dict chứa kết quả kiểm tra
        """
        if self.current_profile is None:
            return {
                "eligible": None,
                "checks": [],
                "reason": "Chưa có thông tin profile"
            }
        
        if not scholarship:
            return {
                "eligible": None,
                "checks": [],
                "reason": "Không có thông tin học bổng"
            }
        
        checks = []
        eligible = True
        
        # Kiểm tra GPA
        if scholarship.get("Min_Gpa") and self.current_profile.gpa:
            checks.append(f"GPA: {self.current_profile.gpa}")
        
        # Kiểm tra tuổi
        if scholarship.get("Age") and self.current_profile.age:
            checks.append(f"Tuổi: {self.current_profile.age}")
        
        # Kiểm tra bằng cấp
        required_degree = scholarship.get("Required_Degree", "")
        if required_degree and self.current_profile.current_degree:
            degree_match = self.current_profile.current_degree.lower() in required_degree.lower()
            if not degree_match:
                eligible = False
                checks.append(f"⚠ Bằng cấp: Yêu cầu {required_degree}, có {self.current_profile.current_degree}")
            else:
                checks.append(f"✓ Bằng cấp phù hợp")
        
        # Kiểm tra ngành học
        eligible_fields = scholarship.get("Eligible_Fields", "")
        if eligible_fields and self.current_profile.target_field:
            field_match = self.current_profile.target_field.lower() in eligible_fields.lower()
            if not field_match:
                checks.append(f"⚠ Ngành học: {self.current_profile.target_field} có thể không phù hợp")
            else:
                checks.append(f"✓ Ngành học phù hợp")
        
        return {
            "eligible": eligible,
            "checks": checks,
            "reason": "\n".join(checks) if checks else "Không đủ thông tin"
        }
