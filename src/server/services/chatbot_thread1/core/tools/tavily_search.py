"""
Tool 3: Dynamic Search - Tìm kiếm động trên Internet sử dụng Tavily API
Refactored to use Langchain BaseTool
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import Field
from tavily import TavilyClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.utils.api_key_manager import get_next_tavily_key

class TavilySearchTool(BaseTool):
    """Tool tìm kiếm thông tin trên Internet sử dụng Tavily API"""
    
    name: str = "tavily_search"
    description: str = """Search for information on the Internet.
    Use when additional information, general advice, or off-topic questions are needed.
    Input: question or topic to search.
    Output: information from the Internet."""
    
    # Custom fields
    client: Any = Field(default=None, exclude=True)
    
    def __init__(self, **kwargs):
        """Khởi tạo Tavily Search Tool"""
        super().__init__(**kwargs)
        # Sử dụng API key rotation
        self.client = TavilyClient(api_key=get_next_tavily_key())
    
    def _run(self, query: str) -> str:
        """
        Langchain BaseTool _run method
        
        Args:
            query: Câu hỏi cần tìm kiếm
            
        Returns:
            String representation của kết quả
        """
        results = self.search(query)
        
        if not results:
            return "Không tìm thấy thông tin phù hợp."
        
        # Format results
        output = []
        for idx, result in enumerate(results, 1):
            title = result.get("title", "No title")
            content = result.get("content", "")[:200]  # Giới hạn 200 chars
            output.append(f"{idx}. {title}\n   {content}...")
        
        return "\n\n".join(output)
    
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
