"""
Main Module - Chatbot Thread 1
Hệ thống chatbot tư vấn học bổng với Intent Routing và Multi-Tool Retrieval
"""
import os
import signal
from typing import Dict, Any, Optional
from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.models.intent import Intent
from services.chatbot_thread1.core.models.user_profile import UserProfile
from services.chatbot_thread1.core.modules.intent_router import IntentRouter
from services.chatbot_thread1.core.modules.response_generator import ResponseGenerator
from services.chatbot_thread1.core.tools.semantic_search import SemanticSearchTool
from services.chatbot_thread1.core.tools.structured_query import StructuredQueryTool
from services.chatbot_thread1.core.tools.tavily_search import TavilySearchTool
from services.chatbot_thread1.core.tools.profile_retriever import ProfileRetrieverTool
from services.chatbot_thread1.core.utils.data_loader import DataLoader
from services.chatbot_thread1.core.utils.context_assembler import ContextAssembler

# Timeout exception
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

class ScholarshipChatbot:
    """
    Chatbot tư vấn học bổng - Thread 1
    """
    
    def __init__(self):
        """Khởi tạo Chatbot với tất cả các components"""
        print("🔄 Đang khởi tạo chatbot...")
        
        # Validate config
        Config.validate()
        
        # Khởi tạo components (silent mode)
        self.data_loader = DataLoader()
        self.semantic_search = SemanticSearchTool()
        self.structured_query = StructuredQueryTool(self.data_loader)
        self.tavily_search = TavilySearchTool()
        self.profile_retriever = ProfileRetrieverTool()
        self.intent_router = IntentRouter()
        self.response_generator = ResponseGenerator()
        
        # Index scholarships (nếu cần)
        use_semantic = os.getenv("USE_SEMANTIC_SEARCH", "true").lower() == "true"
        if use_semantic:
            scholarships = self.data_loader.get_all_scholarships()
            if scholarships:
                try:
                    self.semantic_search.index_scholarships(scholarships)
                except:
                    pass
            
            # Index RAG database
            if self.semantic_search.rag_tool:
                try:
                    self.semantic_search.rag_tool.index_rag_documents()
                except Exception as e:
                    print(f"⚠ Không thể index RAG database: {e}")
        
        print("✅ Chatbot đã sẵn sàng!\n")
    
    def chat(
        self, 
        query: str, 
        profile_enabled: bool = False,
        user_profile: Optional[Dict[str, Any]] = None,
        timeout: int = 180
    ) -> Dict[str, Any]:
        """
        Xử lý một câu hỏi từ người dùng với timeout protection
        
        Args:
            query: Câu hỏi của người dùng
            profile_enabled: Có sử dụng profile hay không (nút ON/OFF)
            user_profile: Dict chứa thông tin profile (nếu có)
            timeout: Thời gian timeout tối đa (giây), mặc định 180s
            
        Returns:
            Dict chứa câu trả lời và metadata
        """
        # Windows không hỗ trợ signal.alarm, dùng threading thay thế
        import threading
        
        result = {"error": None}
        
        def chat_worker():
            try:
                # Load profile nếu có
                profile_obj = None
                if profile_enabled and user_profile:
                    profile_obj = self.profile_retriever.load_profile(user_profile)
                
                # GIAI ĐOẠN 1: INTENT ROUTING
                intent = self.intent_router.classify_intent(query, profile_enabled)
                
                # GIAI ĐOẠN 2: XÁC ĐỊNH TOOLS CẦN SỬ DỤNG
                tools_to_use = self.intent_router.route_to_tools(intent)
                
                # GIAI ĐOẠN 3: RETRIEVAL - GỌI CÁC TOOLS
                
                semantic_results = None
                structured_results = None
                tavily_results = None
                
                # Tool 1: Semantic Search
                use_semantic = os.getenv("USE_SEMANTIC_SEARCH", "true").lower() == "true"
                if tools_to_use.get("semantic_search") and use_semantic:
                    try:
                        semantic_results = self.semantic_search.search(query)
                    except Exception as e:
                        semantic_results = None
                
                # Tool 2: Structured Query
                if tools_to_use.get("structured_query"):
                    try:
                        structured_results = self._execute_structured_query(query, intent)
                    except Exception as e:
                        structured_results = None
                
                # Tool 3: Tavily Search
                if tools_to_use.get("tavily_search"):
                    try:
                        tavily_results = self.tavily_search.search(query)
                    except Exception as e:
                        tavily_results = None
                
                # GIAI ĐOẠN 4: TỔNG HỢP CONTEXT VÀ TẠO SINH CÂU TRẢ LỜI
                context = ContextAssembler.assemble(
                    query=query,
                    semantic_results=semantic_results,
                    structured_results=structured_results,
                    tavily_results=tavily_results,
                    user_profile=profile_obj
                )
                
                # Kiểm tra context length và cảnh báo
                if len(context) > 10000:
                    print(f"⚠ Warning: Context rất dài ({len(context)} chars)")
                
                # Tạo câu trả lời
                answer = self.response_generator.generate(query, context, intent)
                
                # Kiểm tra answer length và cảnh báo
                if len(answer) > 10000:
                    print(f"⚠ Warning: Response từ Gemini rất dài ({len(answer)} chars)")
                
                # Trả về kết quả
                result["data"] = {
                    "query": query,
                    "answer": answer,
                    "intent": intent.intent_type.value,
                    "confidence": intent.confidence,
                    "tools_used": [k for k, v in tools_to_use.items() if v],
                    "metadata": {
                        "semantic_results_count": len(semantic_results) if semantic_results else 0,
                        "structured_results_count": len(structured_results) if structured_results else 0,
                        "tavily_results_count": len(tavily_results) if tavily_results else 0,
                        "has_profile": profile_enabled
                    }
                }
            except Exception as e:
                result["error"] = str(e)
        
        # Chạy chat trong thread với timeout
        thread = threading.Thread(target=chat_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        # Kiểm tra timeout
        if thread.is_alive():
            print(f"❌ TIMEOUT: Chat vượt quá {timeout} giây, dừng xử lý")
            return {
                "query": query,
                "answer": f"Xin lỗi, câu hỏi của bạn mất quá nhiều thời gian xử lý (>{timeout}s). Vui lòng thử lại với câu hỏi ngắn gọn hơn.",
                "intent": "timeout",
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {
                    "timeout": True,
                    "timeout_seconds": timeout
                }
            }
        
        # Kiểm tra lỗi
        if result.get("error"):
            print(f"❌ Error trong chat: {result['error']}")
            return {
                "query": query,
                "answer": f"Xin lỗi, đã xảy ra lỗi: {result['error']}",
                "intent": "error",
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {"error": result["error"]}
            }
        
        return result.get("data", {})
    
    def _execute_structured_query(self, query: str, intent: Intent) -> list:
        """
        Thực thi structured query dựa trên intent và extracted params
        
        Args:
            query: Query gốc
            intent: Intent đã phân loại
            
        Returns:
            List kết quả từ structured query
        """
        params = intent.extracted_params or {}
        
        # Nếu có tên học bổng cụ thể
        if params.get("scholarship_name"):
            scholarship = self.structured_query.get_scholarship_details(params["scholarship_name"])
            return [scholarship] if scholarship else []
        
        # Nếu cần so sánh
        query_str = query if isinstance(query, str) else str(query)
        if "compare" in query_str.lower() or "so sánh" in query_str.lower():
            # TODO: Extract scholarship names để so sánh
            return []
        
        # Lọc theo các tiêu chí
        filters = {}
        if params.get("country"):
            country = params["country"]
            # Xử lý nếu country là list, lấy phần tử đầu
            filters["country"] = country[0] if isinstance(country, list) else country
        if params.get("field"):
            field = params["field"]
            filters["field"] = field[0] if isinstance(field, list) else field
        if params.get("degree"):
            degree = params["degree"]
            filters["degree"] = degree[0] if isinstance(degree, list) else degree
        
        if filters:
            return self.structured_query.advanced_filter(filters)
        
        # Mặc định: trả về tất cả
        return self.structured_query.data_loader.get_all_scholarships()[:10]  # Giới hạn 10
