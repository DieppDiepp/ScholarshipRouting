"""
Scholarship Agent - Agent chính điều phối toàn bộ flow của chatbot
"""
from typing import Dict, Any, Optional, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.core.chains.intent_chain import IntentClassificationChain
from services.chatbot_thread1.core.chains.response_chain import ResponseGenerationChain
from services.chatbot_thread1.core.tools.semantic_search import SemanticSearchTool
from services.chatbot_thread1.core.tools.structured_query import StructuredQueryTool
from services.chatbot_thread1.core.tools.tavily_search import TavilySearchTool
from services.chatbot_thread1.core.tools.profile_retriever import ProfileRetrieverTool
from services.chatbot_thread1.core.utils.context_assembler import ContextAssembler
from services.chatbot_thread1.core.utils.data_loader import DataLoader
from services.chatbot_thread1.core.utils.language_detector import LanguageDetector
from services.chatbot_thread1.core.models.intent import Intent
from services.chatbot_thread1.config import Config


class ScholarshipAgent:
    """
    Agent chính điều phối toàn bộ flow của chatbot
    Sử dụng Langchain chains và tools
    """
    
    def __init__(self):
        """Khởi tạo Scholarship Agent"""
        print("🔄 Đang khởi tạo Scholarship Agent...")
        
        # Validate config
        Config.validate()
        
        # Khởi tạo chains
        self.intent_chain = IntentClassificationChain()
        self.response_chain = ResponseGenerationChain()
        
        # Khởi tạo data loader
        self.data_loader = DataLoader()
        
        # Khởi tạo language detector
        self.language_detector = LanguageDetector()
        
        # Khởi tạo tools
        self.semantic_search = SemanticSearchTool()
        self.structured_query = StructuredQueryTool(self.data_loader)
        self.tavily_search = TavilySearchTool()
        self.profile_retriever = ProfileRetrieverTool()
        
        # Index scholarships nếu cần
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
        
        print("✅ Scholarship Agent đã sẵn sàng!\n")
    
    def run(
        self,
        query: str,
        original_query: str = None,
        profile_enabled: bool = False,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chạy agent để xử lý query
        
        Args:
            query: Câu hỏi của người dùng (có thể đã enhance với history)
            original_query: Query gốc của user (để detect language)
            profile_enabled: Có sử dụng profile hay không
            user_profile: Dict chứa thông tin profile (nếu có)
            
        Returns:
            Dict chứa câu trả lời và metadata
        """
        # Nếu không có original_query, dùng query
        if original_query is None:
            original_query = query
        try:
            # GIAI ĐOẠN 0: LANGUAGE DETECTION
            # Detect language từ original query (không phải enhanced query)
            detected_language = self.language_detector.detect(original_query)
            
            # Load profile nếu có
            profile_obj = None
            if profile_enabled and user_profile:
                profile_obj = self.profile_retriever.load_profile(user_profile)
            
            # GIAI ĐOẠN 1: INTENT CLASSIFICATION
            print(f"📝 Query: {query}")
            intent = self.intent_chain.classify(query, profile_enabled)
            
            # GIAI ĐOẠN 2: TOOL SELECTION
            tools_to_use = self.intent_chain.get_tools_for_intent(intent)
            print(f"🔧 Tools sẽ sử dụng: {[k for k, v in tools_to_use.items() if v]}")
            
            # GIAI ĐOẠN 3: TOOL EXECUTION
            semantic_results = None
            structured_results = None
            tavily_results = None
            
            # Tool 1: Semantic Search
            use_semantic = os.getenv("USE_SEMANTIC_SEARCH", "true").lower() == "true"
            if tools_to_use.get("semantic_search") and use_semantic:
                try:
                    print("  → Đang chạy Semantic Search...")
                    semantic_results = self.semantic_search.search(query)
                except Exception as e:
                    print(f"  ✗ Lỗi Semantic Search: {e}")
                    semantic_results = None
            
            # Tool 2: Structured Query
            if tools_to_use.get("structured_query"):
                try:
                    print("  → Đang chạy Structured Query...")
                    structured_results = self._execute_structured_query(query, intent)
                except Exception as e:
                    print(f"  ✗ Lỗi Structured Query: {e}")
                    structured_results = None
            
            # Tool 3: Tavily Search
            if tools_to_use.get("tavily_search"):
                try:
                    print("  → Đang chạy Tavily Search...")
                    tavily_results = self.tavily_search.search(query)
                except Exception as e:
                    print(f"  ✗ Lỗi Tavily Search: {e}")
                    tavily_results = None
            
            # GIAI ĐOẠN 4: CONTEXT ASSEMBLY
            print("📦 Đang tổng hợp context...")
            context = ContextAssembler.assemble(
                query=query,
                semantic_results=semantic_results,
                structured_results=structured_results,
                tavily_results=tavily_results,
                user_profile=profile_obj
            )
            
            # GIAI ĐOẠN 5: RESPONSE GENERATION
            print(f"🤖 Đang tạo câu trả lời (ngôn ngữ: {detected_language})...")
            answer = self.response_chain.generate(query, context, intent, language=detected_language)
            
            # Trả về kết quả
            return {
                "query": query,
                "answer": answer,
                "intent": intent.intent_type.value,
                "confidence": intent.confidence,
                "language": detected_language,
                "tools_used": [k for k, v in tools_to_use.items() if v],
                "metadata": {
                    "semantic_results_count": len(semantic_results) if semantic_results else 0,
                    "structured_results_count": len(structured_results) if structured_results else 0,
                    "tavily_results_count": len(tavily_results) if tavily_results else 0,
                    "has_profile": profile_enabled,
                    "detected_language": detected_language
                }
            }
            
        except Exception as e:
            print(f"❌ Lỗi trong agent: {e}")
            return {
                "query": query,
                "answer": f"Xin lỗi, đã xảy ra lỗi: {e}",
                "intent": "error",
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {"error": str(e)}
            }
    
    def _execute_structured_query(self, query: str, intent: Intent) -> List[Dict[str, Any]]:
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
        return self.data_loader.get_all_scholarships()[:10]  # Giới hạn 10
