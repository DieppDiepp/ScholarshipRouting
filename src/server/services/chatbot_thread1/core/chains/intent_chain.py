"""
Intent Classification Chain - Phân loại ý định người dùng sử dụng Langchain
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.models.intent import Intent, IntentType
from services.chatbot_thread1.core.utils.api_key_manager import get_next_gemini_key


class IntentClassificationChain:
    """Chain để phân loại intent từ user query"""
    
    def __init__(self):
        """Khởi tạo Intent Classification Chain"""
        # Khởi tạo LLM (Gemini Flash cho classification nhanh)
        # Sử dụng API key rotation
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL_CLASSIFICATION,
            temperature=0.0,  # Deterministic cho classification
            google_api_key=get_next_gemini_key(),
            timeout=60
        )
        
        # Tạo prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "{query}")
        ])
        
        # Output parser
        self.parser = JsonOutputParser()
        
        # Tạo chain
        # Add name for better LangSmith tracing
        self.chain = (self.prompt | self.llm | self.parser).with_config(
            {"run_name": "Intent Classification"}
        )
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt for intent classification"""
        return """You are an intent classification system for a scholarship advisory chatbot.

Task: Analyze the user's question and determine the most appropriate intent.

INTENT TYPES:
1. fact_retrieval: Find details about a specific scholarship
   - Examples: "Tell me about Turkiye Burslari scholarship", "What does Hungary scholarship offer?"
   
2. filtering: Filter/List scholarships by criteria
   - Examples: "Which scholarships in Turkey?", "List full scholarships", "Scholarships for engineering"
   
3. static_comparison: Compare scholarships with each other
   - Examples: "Compare Turkey and Hungary scholarships", "Which scholarship is better?"
   
4. general_advice: General scholarship advice (no profile needed)
   - Examples: "How to apply for scholarships?", "What to prepare for scholarship application?"
   
5. external_qa: Off-topic questions requiring Internet search
   - Examples: "What's life like in Turkey?", "Cost of living in Hungary?"
   
6. personalized_advice: Personalized advice (REQUIRES profile)
   - Examples: "Should I apply for this scholarship?", "Which scholarship suits me?"
   
7. personalized_recommendation: Personalized scholarship recommendations (REQUIRES profile)
   - Examples: "Suggest scholarships for me", "Which scholarship should I apply for?"

Return JSON in this format:
{{
    "intent_type": "intent_name",
    "confidence": 0.95,
    "reasoning": "Classification reason",
    "extracted_params": {{
        "scholarship_name": "scholarship name if any",
        "country": "country if any",
        "field": "field of study if any",
        "degree": "degree level if any",
        "keywords": ["important keywords"]
    }}
}}

RETURN ONLY JSON, NO ADDITIONAL EXPLANATION."""
    
    def classify(self, query: str, has_profile: bool = False) -> Intent:
        """
        Phân loại intent từ query
        
        Args:
            query: Câu hỏi của người dùng
            has_profile: Có profile hay không
            
        Returns:
            Intent object
        """
        try:
            # Add profile information to query context
            query_with_context = f"{query}\n\n[Profile: {'Available' if has_profile else 'Not Available'}]"
            
            # Invoke chain
            result = self.chain.invoke({"query": query_with_context})
            
            # Parse result thành Intent object
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
            # Fallback
            return Intent(
                intent_type=IntentType.GENERAL_ADVICE,
                confidence=0.5,
                extracted_params={}
            )
    
    def get_tools_for_intent(self, intent: Intent) -> Dict[str, bool]:
        """
        Xác định tools nào cần sử dụng dựa trên intent
        
        Args:
            intent: Intent đã được phân loại
            
        Returns:
            Dict mapping tool name -> có sử dụng hay không
        """
        tool_mapping = {
            IntentType.FACT_RETRIEVAL: {
                "semantic_search": True,
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
