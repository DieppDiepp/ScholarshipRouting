"""
Tool 3: Dynamic Search - Tìm kiếm động trên Internet sử dụng Tavily API
"""
from typing import List, Dict, Any
from tavily import TavilyClient
from config import Config

class TavilySearchTool:
    """Tool tìm kiếm thông tin trên Internet sử dụng Tavily API"""
    
    def __init__(self):
        """Khởi tạo Tavily Search Tool"""
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    
    def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm thông tin trên Internet
        
        Args:
            query: Câu hỏi/truy vấn cần tìm kiếm
            max_results: Số lượng kết quả tối đa (mặc định lấy từ Config)
            
        Returns:
            List các kết quả tìm kiếm
        """
        if max_results is None:
            max_results = Config.TAVILY_MAX_RESULTS
        
        try:
            # Gọi Tavily API
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",  # Tìm kiếm sâu hơn
                include_answer=True,  # Bao gồm câu trả lời tóm tắt
                include_raw_content=False  # Không cần raw HTML
            )
            
            # Parse kết quả
            results = []
            if 'results' in response:
                for item in response['results']:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0)
                    })
            
            # Thêm answer nếu có
            if 'answer' in response and response['answer']:
                results.insert(0, {
                    'title': 'Tavily AI Answer',
                    'url': '',
                    'content': response['answer'],
                    'score': 1.0
                })
            
            return results
            
        except Exception as e:
            print(f"✗ Lỗi khi tìm kiếm với Tavily: {e}")
            return []
    
    def search_scholarship_info(self, scholarship_name: str) -> List[Dict[str, Any]]:
        """
        Tìm kiếm thông tin bổ sung về một học bổng cụ thể
        
        Args:
            scholarship_name: Tên học bổng
            
        Returns:
            List các thông tin bổ sung từ Internet
        """
        query = f"{scholarship_name} scholarship requirements application deadline"
        return self.search(query)
    
    def search_general_advice(self, topic: str) -> List[Dict[str, Any]]:
        """
        Tìm kiếm lời khuyên chung về học bổng
        
        Args:
            topic: Chủ đề cần tư vấn
            
        Returns:
            List các thông tin tư vấn
        """
        query = f"scholarship advice {topic}"
        return self.search(query)
    
    def search_country_education(self, country: str) -> List[Dict[str, Any]]:
        """
        Tìm kiếm thông tin về giáo dục ở một quốc gia
        
        Args:
            country: Tên quốc gia
            
        Returns:
            List thông tin về giáo dục ở quốc gia đó
        """
        query = f"study in {country} international students scholarships"
        return self.search(query)
