"""
Module A: Intent Router - Bộ Điều phối Ý định
Phân loại query của người dùng thành các intent khác nhau
"""
import google.generativeai as genai
import threading
from typing import Dict, Any
from core.models.intent import Intent, IntentType
from config import Config
import json

class IntentRouter:
    """Bộ điều phối ý định - Phân loại query thành các intent"""
    
    def __init__(self):
        """Khởi tạo Intent Router"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self._cache = {}  # Simple cache cho intent classification
    
    def classify_intent(self, query: str, has_profile: bool = False) -> Intent:
        """
        Phân loại intent từ query của người dùng
        
        Args:
            query: Câu hỏi của người dùng
            has_profile: Có profile hay không (nút Profile ON/OFF)
            
        Returns:
            Intent object chứa loại intent và các tham số
        """
        # Tạo prompt để phân loại intent
        prompt = f"""
Bạn là một hệ thống phân loại ý định (intent classification) cho chatbot tư vấn học bổng.

Nhiệm vụ: Phân tích câu hỏi của người dùng và xác định intent phù hợp nhất.

CÁC LOẠI INTENT:
1. fact_retrieval: Tìm chi tiết về một học bổng cụ thể
   - Ví dụ: "Cho tôi biết về học bổng Turkiye Burslari", "Học bổng Hungary có những gì?"
   
2. filtering: Lọc/Liệt kê học bổng theo tiêu chí
   - Ví dụ: "Học bổng nào ở Thổ Nhĩ Kỳ?", "Liệt kê học bổng toàn phần", "Học bổng cho ngành kỹ thuật"
   
3. static_comparison: So sánh các học bổng với nhau
   - Ví dụ: "So sánh học bổng Turkey và Hungary", "Học bổng nào tốt hơn?"
   
4. general_advice: Tư vấn chung về học bổng (không cần profile)
   - Ví dụ: "Làm thế nào để xin học bổng?", "Cần chuẩn bị gì để apply học bổng?"
   
5. external_qa: Hỏi đáp ngoài luồng, cần tìm kiếm Internet
   - Ví dụ: "Cuộc sống ở Thổ Nhĩ Kỳ như thế nào?", "Chi phí sinh hoạt ở Hungary?"
   
6. personalized_advice: Tư vấn cá nhân hóa (CẦN profile)
   - Ví dụ: "Tôi có nên apply học bổng này không?", "Học bổng nào phù hợp với tôi?"
   
7. personalized_recommendation: Đề xuất học bổng cá nhân hóa (CẦN profile)
   - Ví dụ: "Gợi ý học bổng cho tôi", "Tôi nên apply học bổng nào?"

THÔNG TIN BỔ SUNG:
- Người dùng {"ĐÃ" if has_profile else "CHƯA"} bật Profile
- Nếu chưa có profile mà câu hỏi cần profile, hãy chọn intent phù hợp nhất không cần profile

CÂU HỎI CỦA NGƯỜI DÙNG:
"{query}"

Hãy trả về JSON với format sau:
{{
    "intent_type": "tên_intent",
    "confidence": 0.95,
    "reasoning": "Lý do phân loại",
    "extracted_params": {{
        "scholarship_name": "tên học bổng nếu có",
        "country": "quốc gia nếu có",
        "field": "ngành học nếu có",
        "degree": "bậc học nếu có",
        "keywords": ["từ khóa quan trọng"]
    }}
}}

CHỈ TRẢ VỀ JSON, KHÔNG GIẢI THÍCH THÊM.
"""
        
        try:
            # Gọi Gemini API với timeout 60 giây
            result = {"response": None, "error": None}
            
            def api_call():
                try:
                    result["response"] = self.model.generate_content(prompt)
                except Exception as e:
                    result["error"] = str(e)
            
            thread = threading.Thread(target=api_call)
            thread.daemon = True
            thread.start()
            thread.join(timeout=60)  # Timeout 60 giây cho API call
            
            # Kiểm tra timeout
            if thread.is_alive():
                print("❌ TIMEOUT: Intent classification vượt quá 60 giây")
                # Fallback: trả về general_advice
                return Intent(
                    intent_type=IntentType.GENERAL_ADVICE,
                    confidence=0.5,
                    extracted_params={}
                )
            
            # Kiểm tra lỗi
            if result["error"]:
                print(f"✗ Lỗi khi gọi Gemini API: {result['error']}")
                return Intent(
                    intent_type=IntentType.GENERAL_ADVICE,
                    confidence=0.5,
                    extracted_params={}
                )
            
            response = result["response"]
            response_text = response.text.strip()
            
            # Parse JSON response
            # Loại bỏ markdown code block nếu có
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # Tạo Intent object
            intent_type_str = result.get("intent_type", "general_advice")
            intent_type = IntentType(intent_type_str)
            
            intent = Intent(
                intent_type=intent_type,
                confidence=result.get("confidence", 0.8),
                extracted_params=result.get("extracted_params", {})
            )
            
            print(f"✓ Đã phân loại intent: {intent}")
            return intent
            
        except Exception as e:
            print(f"✗ Lỗi khi phân loại intent: {e}")
            # Fallback: trả về general_advice
            return Intent(
                intent_type=IntentType.GENERAL_ADVICE,
                confidence=0.5,
                extracted_params={}
            )
    
    def route_to_tools(self, intent: Intent) -> Dict[str, bool]:
        """
        Xác định tools nào cần sử dụng dựa trên intent
        
        Args:
            intent: Intent đã được phân loại
            
        Returns:
            Dict mapping tool name -> có sử dụng hay không
        """
        # Mapping theo sơ đồ mermaid
        # RAG database được sử dụng trong semantic_search cho fact_retrieval và external_qa
        tool_mapping = {
            IntentType.FACT_RETRIEVAL: {
                "semantic_search": True,  # Sử dụng RAG database
                "structured_query": False,
                "tavily_search": False,
                "profile_retriever": False
            },
            IntentType.FILTERING: {
                "semantic_search": False,
                "structured_query": True,
                "tavily_search": False,
                "profile_retriever": False
            },
            IntentType.STATIC_COMPARISON: {
                "semantic_search": False,
                "structured_query": True,
                "tavily_search": False,
                "profile_retriever": False
            },
            IntentType.GENERAL_ADVICE: {
                "semantic_search": False,
                "structured_query": False,
                "tavily_search": True,
                "profile_retriever": False
            },
            IntentType.EXTERNAL_QA: {
                "semantic_search": False,
                "structured_query": False,
                "tavily_search": True,
                "profile_retriever": False
            },
            IntentType.PERSONALIZED_ADVICE: {
                "semantic_search": False,
                "structured_query": False,
                "tavily_search": True,
                "profile_retriever": True
            },
            IntentType.PERSONALIZED_RECOMMENDATION: {
                "semantic_search": False,
                "structured_query": True,
                "tavily_search": False,
                "profile_retriever": True
            }
        }
        
        return tool_mapping.get(intent.intent_type, {
            "semantic_search": False,
            "structured_query": False,
            "tavily_search": False,
            "profile_retriever": False
        })
