"""
Module tải và xử lý dữ liệu học bổng
"""
import json
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config

class DataLoader:
    """Class quản lý việc tải và truy xuất dữ liệu học bổng"""
    
    def __init__(self, data_path: str = None):
        """
        Khởi tạo DataLoader
        
        Args:
            data_path: Đường dẫn đến file JSON chứa dữ liệu học bổng
        """
        self.data_path = data_path or Config.DATA_PATH
        self.scholarships = []
        self.load_data()
    
    def load_data(self):
        """Tải dữ liệu từ file JSON"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.scholarships = json.load(f)
        except FileNotFoundError:
            print(f"✗ Không tìm thấy file dữ liệu: {self.data_path}")
            self.scholarships = []
        except json.JSONDecodeError as e:
            print(f"✗ Lỗi đọc file JSON: {e}")
            self.scholarships = []
    
    def get_all_scholarships(self) -> List[Dict[str, Any]]:
        """Lấy tất cả học bổng"""
        return self.scholarships
    
    def get_scholarship_by_name(self, name: str) -> Dict[str, Any]:
        """
        Tìm học bổng theo tên
        
        Args:
            name: Tên học bổng cần tìm
            
        Returns:
            Dict chứa thông tin học bổng hoặc None nếu không tìm thấy
        """
        for scholarship in self.scholarships:
            scholarship_name = scholarship.get("Scholarship_Name", "")
            # Xử lý trường hợp scholarship_name là list
            if isinstance(scholarship_name, list):
                scholarship_name = " ".join(str(n) for n in scholarship_name)
            else:
                scholarship_name = str(scholarship_name)
            
            if scholarship_name.lower() == name.lower():
                return scholarship
        return None
    
    def filter_scholarships(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Lọc học bổng theo các tiêu chí
        
        Args:
            filters: Dict chứa các tiêu chí lọc
                Ví dụ: {"Country": "Turkey", "Funding_Level": "Full scholarship"}
        
        Returns:
            List các học bổng phù hợp
        """
        results = []
        
        for scholarship in self.scholarships:
            match = True
            
            for key, value in filters.items():
                # Kiểm tra xem field có tồn tại không
                if key not in scholarship:
                    match = False
                    break
                
                # So sánh giá trị (case-insensitive cho string)
                scholarship_value = scholarship[key]
                if isinstance(scholarship_value, str) and isinstance(value, str):
                    if value.lower() not in scholarship_value.lower():
                        match = False
                        break
                elif scholarship_value != value:
                    match = False
                    break
            
            if match:
                results.append(scholarship)
        
        return results
    
    def get_countries(self) -> List[str]:
        """Lấy danh sách tất cả các quốc gia có học bổng"""
        countries = set()
        for scholarship in self.scholarships:
            country = scholarship.get("Country")
            if country:
                countries.add(country)
        return sorted(list(countries))
    
    def get_fields(self) -> List[str]:
        """Lấy danh sách tất cả các ngành học"""
        fields = set()
        for scholarship in self.scholarships:
            field_str = scholarship.get("Eligible_Fields", "")
            if field_str:
                # Tách các ngành học (phân cách bằng dấu phẩy)
                field_list = [f.strip() for f in field_str.split(",")]
                fields.update(field_list)
        return sorted(list(fields))
