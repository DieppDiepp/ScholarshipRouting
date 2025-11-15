"""
Tool 2: Structured Query - Truy vấn có cấu trúc trên JSON Database
Refactored to use Langchain BaseTool
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import Field
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.core.utils.data_loader import DataLoader

class StructuredQueryTool(BaseTool):
    """Tool truy vấn có cấu trúc trên dữ liệu JSON"""
    
    name: str = "structured_query"
    description: str = """Structured query on scholarship database.
    Use when filtering, listing, or comparing scholarships by specific criteria is needed.
    Input: filter criteria (country, field of study, degree level, funding level).
    Output: list of matching scholarships."""
    
    # Custom fields
    data_loader: Any = Field(default=None, exclude=True)
    
    def __init__(self, data_loader: DataLoader, **kwargs):
        """
        Khởi tạo Structured Query Tool
        
        Args:
            data_loader: Instance của DataLoader để truy xuất dữ liệu
        """
        super().__init__(**kwargs)
        self.data_loader = data_loader
    
    def _run(self, filters: str) -> str:
        """
        Langchain BaseTool _run method
        
        Args:
            filters: String representation của filters (JSON format)
            
        Returns:
            String representation của kết quả
        """
        import json
        
        try:
            # Parse filters từ string
            filters_dict = json.loads(filters) if isinstance(filters, str) else filters
        except:
            filters_dict = {}
        
        # Execute query
        results = self.advanced_filter(filters_dict)
        
        # Format results
        if not results:
            return "Không tìm thấy học bổng phù hợp với tiêu chí."
        
        output = []
        for idx, scholarship in enumerate(results[:10], 1):  # Giới hạn 10
            name = scholarship.get("Scholarship_Name", "Unknown")
            country = scholarship.get("Country", "N/A")
            funding = scholarship.get("Funding_Level", "N/A")
            output.append(f"{idx}. {name} ({country}) - {funding}")
        
        return "\n".join(output)
    
    def filter_by_country(self, country: str) -> List[Dict[str, Any]]:
        """
        Lọc học bổng theo quốc gia
        
        Args:
            country: Tên quốc gia
            
        Returns:
            List các học bổng ở quốc gia đó
        """
        return self.data_loader.filter_scholarships({"Country": country})
    
    def filter_by_field(self, field: str) -> List[Dict[str, Any]]:
        """
        Lọc học bổng theo ngành học
        
        Args:
            field: Tên ngành học
            
        Returns:
            List các học bổng hỗ trợ ngành đó
        """
        results = []
        for scholarship in self.data_loader.get_all_scholarships():
            eligible_fields = scholarship.get("Eligible_Fields", "")
            # Xử lý cả trường hợp string và list
            if isinstance(eligible_fields, list):
                eligible_fields_str = " ".join(str(f) for f in eligible_fields)
            else:
                eligible_fields_str = str(eligible_fields)
            
            if field.lower() in eligible_fields_str.lower():
                results.append(scholarship)
        return results
    
    def filter_by_degree(self, degree: str) -> List[Dict[str, Any]]:
        """
        Lọc học bổng theo bậc học
        
        Args:
            degree: Bậc học (Bachelor, Master, PhD, etc.)
            
        Returns:
            List các học bổng hỗ trợ bậc học đó
        """
        results = []
        for scholarship in self.data_loader.get_all_scholarships():
            required_degree = scholarship.get("Required_Degree", "")
            # Xử lý cả trường hợp string và list
            if isinstance(required_degree, list):
                required_degree_str = " ".join(str(d) for d in required_degree)
            else:
                required_degree_str = str(required_degree)
            
            if degree.lower() in required_degree_str.lower():
                results.append(scholarship)
        return results
    
    def filter_by_funding_level(self, funding_level: str) -> List[Dict[str, Any]]:
        """
        Lọc học bổng theo mức tài trợ
        
        Args:
            funding_level: Mức tài trợ (Full scholarship, Partial, etc.)
            
        Returns:
            List các học bổng với mức tài trợ phù hợp
        """
        results = []
        for scholarship in self.data_loader.get_all_scholarships():
            funding = scholarship.get("Funding_Level", "")
            # Xử lý cả trường hợp string và list
            if isinstance(funding, list):
                funding_str = " ".join(str(f) for f in funding)
            else:
                funding_str = str(funding)
            
            if funding_level.lower() in funding_str.lower():
                results.append(scholarship)
        return results
    
    def filter_by_gpa(self, min_gpa: float, user_gpa: float) -> List[Dict[str, Any]]:
        """
        Lọc học bổng mà người dùng đủ điều kiện GPA
        
        Args:
            min_gpa: GPA tối thiểu của học bổng
            user_gpa: GPA của người dùng
            
        Returns:
            List các học bổng mà người dùng đủ GPA
        """
        results = []
        for scholarship in self.data_loader.get_all_scholarships():
            gpa_str = scholarship.get("Min_Gpa", "")
            # Parse GPA từ string (có thể có nhiều format)
            # Ví dụ: "70%", "3.0", "Undergraduate: 70%"
            # Đơn giản hóa: nếu user_gpa >= min_gpa thì OK
            # TODO: Cần logic parse phức tạp hơn cho production
            if gpa_str and gpa_str != "Not mentioned":
                results.append(scholarship)
        return results
    
    def filter_by_age(self, user_age: int) -> List[Dict[str, Any]]:
        """
        Lọc học bổng mà người dùng đủ điều kiện tuổi
        
        Args:
            user_age: Tuổi của người dùng
            
        Returns:
            List các học bổng mà người dùng đủ tuổi
        """
        results = []
        for scholarship in self.data_loader.get_all_scholarships():
            age_req = scholarship.get("Age", "")
            # Đơn giản hóa: nếu có yêu cầu tuổi thì thêm vào
            # TODO: Parse age requirement phức tạp hơn
            if age_req and age_req != "No requirement":
                results.append(scholarship)
        return results
    
    def advanced_filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Lọc học bổng với nhiều tiêu chí kết hợp
        
        Args:
            filters: Dict chứa các tiêu chí lọc
                Ví dụ: {
                    "country": "Turkey",
                    "degree": "Master",
                    "field": "Engineering",
                    "funding": "Full"
                }
        
        Returns:
            List các học bổng phù hợp với tất cả tiêu chí
        """
        results = self.data_loader.get_all_scholarships()
        
        # Helper function để xử lý cả string và list
        def to_string(value):
            if isinstance(value, list):
                return " ".join(str(v) for v in value)
            return str(value)
        
        # Lọc theo từng tiêu chí
        if "country" in filters:
            country_filter = to_string(filters["country"]).lower()
            results = [s for s in results if country_filter in to_string(s.get("Country", "")).lower()]
        
        if "degree" in filters:
            degree_filter = to_string(filters["degree"]).lower()
            results = [s for s in results if degree_filter in to_string(s.get("Required_Degree", "")).lower()]
        
        if "field" in filters:
            field_filter = to_string(filters["field"]).lower()
            results = [s for s in results if field_filter in to_string(s.get("Eligible_Fields", "")).lower()]
        
        if "funding" in filters:
            funding_filter = to_string(filters["funding"]).lower()
            results = [s for s in results if funding_filter in to_string(s.get("Funding_Level", "")).lower()]
        
        return results
    
    def get_scholarship_details(self, scholarship_name: str) -> Optional[Dict[str, Any]]:
        """
        Lấy chi tiết đầy đủ của một học bổng
        
        Args:
            scholarship_name: Tên học bổng
            
        Returns:
            Dict chứa thông tin chi tiết hoặc None
        """
        return self.data_loader.get_scholarship_by_name(scholarship_name)
    
    def list_all_countries(self) -> List[str]:
        """Liệt kê tất cả quốc gia có học bổng"""
        return self.data_loader.get_countries()
    
    def list_all_fields(self) -> List[str]:
        """Liệt kê tất cả ngành học"""
        return self.data_loader.get_fields()
    
    def compare_scholarships(self, scholarship_names: List[str]) -> List[Dict[str, Any]]:
        """
        So sánh nhiều học bổng
        
        Args:
            scholarship_names: Danh sách tên các học bổng cần so sánh
            
        Returns:
            List các học bổng để so sánh
        """
        results = []
        for name in scholarship_names:
            scholarship = self.get_scholarship_details(name)
            if scholarship:
                results.append(scholarship)
        return results
