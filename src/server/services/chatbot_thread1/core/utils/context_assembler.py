"""
Module tổng hợp context từ nhiều nguồn
"""
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.core.models.user_profile import UserProfile

class ContextAssembler:
    """Class tổng hợp context từ các tools khác nhau"""
    
    # Giới hạn số lượng kết quả để tránh vượt token limit
    MAX_SEMANTIC_RESULTS = 5  # Top 5 semantic search results
    MAX_STRUCTURED_RESULTS = 10  # Top 10 filtered scholarships
    MAX_TAVILY_RESULTS = 3  # Top 3 web sources
    MAX_FIELD_LENGTH = 150  # Max length cho mỗi field
    MAX_RAG_CONTENT = 200  # Max length cho RAG content snippet
    
    @staticmethod
    def assemble(
        query: str,
        semantic_results: Optional[List[Dict[str, Any]]] = None,
        structured_results: Optional[List[Dict[str, Any]]] = None,
        tavily_results: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[UserProfile] = None
    ) -> str:
        """
        Tổng hợp context từ các nguồn khác nhau
        
        Args:
            query: Câu hỏi của người dùng
            semantic_results: Kết quả từ semantic search
            structured_results: Kết quả từ structured query
            tavily_results: Kết quả từ Tavily search
            user_profile: Profile của người dùng
            
        Returns:
            Context string đã được tổng hợp
        """
        context_parts = []
        
        # Original query
        context_parts.append(f"=== QUESTION ===\n{query}\n")
        
        # User profile
        if user_profile:
            profile_str = user_profile.to_context_string()
            if profile_str != "No profile information":
                context_parts.append(f"=== USER PROFILE ===\n{profile_str}\n")
        
        # Semantic search results
        if semantic_results:
            unique_results = ContextAssembler._deduplicate_scholarships(semantic_results)
            
            # Giới hạn số lượng
            limited_semantic = unique_results[:ContextAssembler.MAX_SEMANTIC_RESULTS]
            
            context_parts.append(f"=== SCHOLARSHIPS FROM DATABASE (Semantic Search) ===")
            context_parts.append(f"Top {len(limited_semantic)} most relevant:\n")
            
            for idx, result in enumerate(limited_semantic, 1):
                scholarship_context = ContextAssembler._format_scholarship(result, idx)
                context_parts.append(scholarship_context)
            
            context_parts.append("")
        
        # Structured query results
        if structured_results:
            # Giới hạn số lượng kết quả
            limited_results = structured_results[:ContextAssembler.MAX_STRUCTURED_RESULTS]
            total_count = len(structured_results)
            
            context_parts.append(f"=== FILTERED RESULTS (Structured Query) ===")
            context_parts.append(f"Found {total_count} scholarships. Showing top {len(limited_results)}:\n")
            
            for idx, result in enumerate(limited_results, 1):
                name = result.get("Scholarship_Name", "Unknown")
                country = result.get("Country", "N/A")
                
                # Rút gọn country nếu quá dài
                if len(country) > 100:
                    country = country[:100] + "..."
                
                funding = result.get("Funding_Level", "N/A")
                deadline = result.get("End_Date", "N/A")
                
                # Format ngắn gọn hơn
                context_parts.append(f"{idx}. {name} ({country})")
                context_parts.append(f"   Funding: {funding} | Deadline: {deadline}")
            
            # Thông báo nếu có nhiều hơn
            if total_count > ContextAssembler.MAX_STRUCTURED_RESULTS:
                context_parts.append(f"\n... and {total_count - ContextAssembler.MAX_STRUCTURED_RESULTS} more scholarships")
            
            context_parts.append("")
        
        # Tavily search results
        if tavily_results:
            # Giới hạn số lượng
            limited_tavily = tavily_results[:ContextAssembler.MAX_TAVILY_RESULTS]
            
            context_parts.append(f"=== INFORMATION FROM INTERNET (Tavily) ===")
            context_parts.append(f"Top {len(limited_tavily)} sources:\n")
            
            for idx, result in enumerate(limited_tavily, 1):
                title = result.get("title", "No title")
                content = result.get("content", "")[:200]  # Giảm từ 300 xuống 200
                url = result.get("url", "")
                
                context_parts.append(f"{idx}. {title}")
                if content:
                    context_parts.append(f"   {content}...")
                if url:
                    context_parts.append(f"   🔗 {url}")
            
            context_parts.append("")
        
        # Assemble final context
        final_context = "\n".join(context_parts)
        
        # Log context size
        context_length = len(final_context)
        context_tokens_estimate = context_length // 4  # Rough estimate: 1 token ≈ 4 chars
        print(f"📊 Context: {context_length} chars (~{context_tokens_estimate} tokens)")
        
        return final_context
    
    @staticmethod
    def _deduplicate_scholarships(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Loại bỏ học bổng trùng lặp dựa trên tên"""
        seen = set()
        unique = []
        
        for result in results:
            name = result.get("Scholarship_Name", "Unknown")
            if name not in seen:
                seen.add(name)
                unique.append(result)
        
        return unique
    
    @staticmethod
    def _deduplicate_scholarships(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Loại bỏ học bổng trùng lặp dựa trên tên"""
        seen = set()
        unique = []
        
        for result in results:
            name = result.get("Scholarship_Name", "Unknown")
            if name not in seen:
                seen.add(name)
                unique.append(result)
        
        return unique
    
    @staticmethod
    def _format_scholarship(scholarship: Dict[str, Any], index: int) -> str:
        """Format thông tin học bổng (tối ưu, ngắn gọn)"""
        name = scholarship.get("Scholarship_Name", "Unknown")
        parts = [f"\n{index}. {name}"]
        
        # Chỉ hiển thị các field QUAN TRỌNG NHẤT
        critical_fields = {
            "Country": "Country",
            "Funding_Level": "Funding",
            "End_Date": "Deadline",
            "Required_Degree": "Degree",
            "Min_Gpa": "Min GPA",
            "Language_Certificate": "Language",
            "Eligible_Fields": "Fields"
        }
        
        for field, label in critical_fields.items():
            value = scholarship.get(field)
            if value and value not in ["Not specified", "Not mentioned", "", "N/A"]:
                # Rút gọn nếu quá dài
                if isinstance(value, str) and len(value) > ContextAssembler.MAX_FIELD_LENGTH:
                    value = value[:ContextAssembler.MAX_FIELD_LENGTH] + "..."
                parts.append(f"   {label}: {value}")
        
        # Thêm URL nếu có
        if scholarship.get("Url"):
            parts.append(f"   🔗 {scholarship['Url']}")
        
        # Thêm snippet từ RAG content (rất ngắn)
        if scholarship.get("RAG_Content"):
            content = scholarship['RAG_Content'][:ContextAssembler.MAX_RAG_CONTENT].strip()
            if content:
                parts.append(f"   📄 {content}...")
        
        return "\n".join(parts)
    
    @staticmethod
    def format_for_comparison(scholarships: List[Dict[str, Any]]) -> str:
        """
        Format dữ liệu để so sánh các học bổng
        
        Args:
            scholarships: Danh sách các học bổng cần so sánh
            
        Returns:
            Chuỗi đã format để dễ so sánh
        """
        if not scholarships:
            return "Không có học bổng nào để so sánh."
        
        comparison_fields = [
            "Scholarship_Name", "Country", "Funding_Level",
            "End_Date", "Min_Gpa", "Language_Certificate",
            "Age", "Required_Degree", "Eligible_Fields"
        ]
        
        result = "=== SO SÁNH CÁC HỌC BỔNG ===\n\n"
        
        for field in comparison_fields:
            result += f"## {field}\n"
            for scholarship in scholarships:
                name = scholarship.get("Scholarship_Name", "Unknown")
                value = scholarship.get(field, "N/A")
                result += f"- {name}: {value}\n"
            result += "\n"
        
        return result
