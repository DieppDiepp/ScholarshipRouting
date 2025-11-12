"""
Module tổng hợp context từ nhiều nguồn
"""
from typing import List, Dict, Any, Optional
from core.models.user_profile import UserProfile

class ContextAssembler:
    """Class tổng hợp context từ các tools khác nhau"""
    
    @staticmethod
    def assemble(
        query: str,
        semantic_results: Optional[List[Dict[str, Any]]] = None,
        structured_results: Optional[List[Dict[str, Any]]] = None,
        tavily_results: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[UserProfile] = None
    ) -> str:
        """
        Tổng hợp tất cả context thành một chuỗi duy nhất
        
        Args:
            query: Câu hỏi của người dùng
            semantic_results: Kết quả từ semantic search
            structured_results: Kết quả từ structured query
            tavily_results: Kết quả từ Tavily search
            user_profile: Profile của người dùng
            
        Returns:
            Chuỗi context đã được tổng hợp
        """
        context_parts = []
        
        # Thêm query gốc
        context_parts.append(f"=== CÂU HỎI CỦA NGƯỜI DÙNG ===\n{query}\n")
        
        # Thêm profile nếu có
        if user_profile:
            profile_str = user_profile.to_context_string()
            if profile_str != "Không có thông tin profile":
                context_parts.append(f"=== THÔNG TIN PROFILE NGƯỜI DÙNG ===\n{profile_str}\n")
        
        # Thêm kết quả semantic search (loại bỏ duplicate)
        if semantic_results:
            # Loại bỏ học bổng trùng lặp dựa trên tên
            seen_scholarships = set()
            unique_results = []
            for result in semantic_results:
                name = result.get("Scholarship_Name", "Unknown")
                if name not in seen_scholarships:
                    seen_scholarships.add(name)
                    unique_results.append(result)
            
            context_parts.append("=== THÔNG TIN HỌC BỔNG TỪ CƠ SỞ DỮ LIỆU (Semantic Search) ===")
            for idx, result in enumerate(unique_results, 1):
                scholarship_name = result.get("Scholarship_Name", "Unknown")
                context_parts.append(f"\n--- Học bổng {idx}: {scholarship_name} ---")
                
                # Thêm các thông tin quan trọng
                important_fields = [
                    "Country", "Funding_Level", "Funding_Details",
                    "End_Date", "Eligibility_Criteria", "Eligible_Fields",
                    "Required_Degree", "Min_Gpa", "Language_Certificate",
                    "Age", "Scholarship_Info", "Url"
                ]
                
                for field in important_fields:
                    value = result.get(field)
                    if value and value != "Not specified" and value != "Not mentioned":
                        context_parts.append(f"{field}: {value}")
                
                # Thêm RAG info nếu có (URL + web content)
                if result.get("RAG_URL"):
                    context_parts.append(f"🔗 Source URL: {result['RAG_URL']}")
                
                if result.get("RAG_Content"):
                    context_parts.append(f"📄 Additional Info from Web: {result['RAG_Content'][:300]}...")
            
            context_parts.append("")
        
        # Thêm kết quả structured query
        if structured_results:
            context_parts.append("=== KẾT QUẢ LỌC/TÌM KIẾM CÓ CẤU TRÚC ===")
            for idx, result in enumerate(structured_results, 1):
                scholarship_name = result.get("Scholarship_Name", "Unknown")
                context_parts.append(f"\n{idx}. {scholarship_name}")
                
                # Hiển thị thông tin tóm tắt
                country = result.get("Country", "N/A")
                funding = result.get("Funding_Level", "N/A")
                deadline = result.get("End_Date", "N/A")
                context_parts.append(f"   - Quốc gia: {country}")
                context_parts.append(f"   - Mức tài trợ: {funding}")
                context_parts.append(f"   - Hạn nộp: {deadline}")
            context_parts.append("")
        
        # Thêm kết quả Tavily (thông tin bên ngoài)
        if tavily_results:
            context_parts.append("=== THÔNG TIN BỔ SUNG TỪ INTERNET (Tavily Search) ===")
            for idx, result in enumerate(tavily_results, 1):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "")
                
                context_parts.append(f"\n{idx}. {title}")
                context_parts.append(f"   Nội dung: {content[:300]}...")  # Giới hạn 300 ký tự
                if url:
                    context_parts.append(f"   Nguồn: {url}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
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
