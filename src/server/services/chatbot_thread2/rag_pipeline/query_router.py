"""
Query Router Module - Phân loại query trước khi quyết định có cần chạy RAG pipeline không.

Best Practice: Tiết kiệm API calls và thời gian bằng cách lọc các query đơn giản.
"""

from langchain_core.prompts import ChatPromptTemplate
from google.api_core.exceptions import ResourceExhausted
import logging

from .. import config
from .llm_factory import get_next_api_key, _create_llm_with_retry
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# --- ROUTER PROMPT ---
router_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an intelligent query classifier for a study abroad scholarship chatbot system.\n"
     "Your task is to classify the user's query into ONE of these categories:\n\n"
     
     "1. **greeting**: Simple greetings or introductions\n"
     "   - Examples: 'hello', 'hi there', 'xin chào', 'chào bạn', 'good morning'\n\n"
     
     "2. **scholarship_search**: Questions about scholarships, studying abroad, funding, applications, eligibility\n"
     "   - Examples: 'find scholarships in Europe', 'học bổng thạc sĩ', 'how to apply', 'tôi muốn du học úc'\n\n"
     
     "3. **chitchat**: Casual conversation, thanks, small talk (NOT scholarship related)\n"
     "   - Examples: 'cảm ơn bạn', 'that's helpful', 'how are you', 'bạn khỏe không'\n\n"
     
     "4. **off_topic**: Questions completely unrelated to scholarships or education\n"
     "   - Examples: 'what's the weather', 'solve this math problem', 'thời tiết hôm nay'\n\n"
     
     "IMPORTANT RULES:\n"
     "- If the query mentions ANY scholarship/study abroad keyword → classify as 'scholarship_search'\n"
     "- If the query is a follow-up like 'tell me more about it' → classify as 'scholarship_search'\n"
     "- Be strict: only pure greetings get 'greeting', only pure thanks/chitchat get 'chitchat'\n"
     "- Provide clear reasoning for your classification."
    ),
    ("human", "Classify this query: {user_query}")
])

def get_router_llm() -> ChatGoogleGenerativeAI:
    """
    Tạo LLM cho Router (sử dụng API key rotation với auto-retry).
    """
    def creator(api_key: str) -> ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(
            model=config.ROUTER_LLM_MODEL,
            google_api_key=api_key,
            temperature=config.ROUTER_LLM_TEMP
        )
        return llm.with_structured_output(config.QueryClassification)
    return _create_llm_with_retry(creator)

def classify_query(user_query: str) -> config.QueryClassification:
    """
    Phân loại query của user với retry logic.
    Tự động skip key hết quota và thử key tiếp theo.
    
    Args:
        user_query: Câu hỏi gốc của user (có thể tiếng Việt hoặc tiếng Anh)
        
    Returns:
        QueryClassification object với query_type và reasoning
    """
    logger.info(f"--- [ROUTER] Classifying query: '{user_query[:100]}...' ---")
    
    from .llm_factory import API_KEY_POOL
    max_attempts = len(API_KEY_POOL)
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            # Tạo LLM và chain MỚI mỗi lần thử
            router_llm = get_router_llm()
            router_chain = router_prompt | router_llm
            
            # Invoke chain
            classification = router_chain.invoke({"user_query": user_query})
            
            logger.info(f"--- [ROUTER] Classification: {classification.query_type} ---")
            logger.info(f"--- [ROUTER] Reasoning: {classification.reasoning} ---")
            
            return classification
            
        except ResourceExhausted as e:
            last_error = e
            logger.warning(
                f"⚠️ [ROUTER] API Key hết quota (429). "
                f"Thử key tiếp theo... (Attempt {attempt + 1}/{max_attempts})"
            )
            
            if attempt < max_attempts - 1:
                continue  # Thử lại với key mới
            else:
                # Đã thử hết tất cả keys
                logger.error(f"❌ [ROUTER] TẤT CẢ {max_attempts} API keys đều hết quota!")
                raise ResourceExhausted(
                    f"All API keys exceeded quota. Please check billing."
                ) from last_error
                
        except Exception as e:
            # Lỗi khác không retry
            logger.error(f"❌ [ROUTER] Lỗi không mong muốn: {e}")
            raise
    
    # Fallback (không nên reach được đây)
    raise RuntimeError("classify_query: Unexpected state")

def should_use_rag(classification: config.QueryClassification) -> bool:
    """
    Quyết định có cần chạy RAG pipeline không.
    
    Returns:
        True: Cần query vector store và chạy full RAG
        False: Không cần RAG, trả lời trực tiếp
    """
    # Chỉ scholarship_search mới cần RAG
    needs_rag = classification.query_type == "scholarship_search"
    
    logger.info(f"--- [ROUTER] Needs RAG: {needs_rag} ---")
    return needs_rag

# --- DIRECT RESPONSES (Không cần RAG) ---
GREETING_RESPONSES = {
    "vi": (
        "Xin chào! 👋 Tôi là trợ lý tư vấn du học. "
        "Tôi có thể giúp bạn tìm kiếm học bổng phù hợp với nhu cầu của bạn. "
        "Hãy cho tôi biết bạn quan tâm đến học bổng nào nhé!"
    ),
    "en": (
        "Hello! 👋 I'm your study abroad advisor. "
        "I can help you find scholarships that match your needs. "
        "Please tell me what kind of scholarship you're looking for!"
    )
}

CHITCHAT_RESPONSES = {
    "vi": (
        "Cảm ơn bạn! 😊 Nếu bạn cần tìm hiểu thêm về học bổng hoặc du học, "
        "đừng ngại hỏi tôi nhé!"
    ),
    "en": (
        "Thank you! 😊 If you need more information about scholarships or studying abroad, "
        "feel free to ask me!"
    )
}

OFF_TOPIC_RESPONSES = {
    "vi": (
        "Xin lỗi, tôi là chatbot chuyên về tư vấn học bổng và du học. "
        "Tôi không thể trả lời câu hỏi này. "
        "Bạn có thắc mắc gì về học bổng không? 🎓"
    ),
    "en": (
        "I'm sorry, I'm a chatbot specialized in scholarship and study abroad advising. "
        "I can't answer this question. "
        "Do you have any questions about scholarships? 🎓"
    )
}

def get_direct_response(classification: config.QueryClassification, user_query: str) -> str:
    """
    Tạo câu trả lời trực tiếp cho các query không cần RAG.
    
    Args:
        classification: Kết quả phân loại từ router
        user_query: Query gốc (để detect ngôn ngữ)
        
    Returns:
        Câu trả lời phù hợp
    """
    # Detect ngôn ngữ đơn giản (có thể cải thiện)
    is_vietnamese = any(char in user_query for char in "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ")
    lang = "vi" if is_vietnamese else "en"
    
    query_type = classification.query_type
    
    if query_type == "greeting":
        return GREETING_RESPONSES[lang]
    elif query_type == "chitchat":
        return CHITCHAT_RESPONSES[lang]
    elif query_type == "off_topic":
        return OFF_TOPIC_RESPONSES[lang]
    else:
        # Fallback (không nên xảy ra)
        return GREETING_RESPONSES[lang]

if __name__ == '__main__':
    # Test router
    test_queries = [
        "xin chào bạn",
        "hello there",
        "tôi muốn tìm học bổng thạc sĩ ở châu âu",
        "I want to find a scholarship in USA",
        "cảm ơn bạn nhiều",
        "thời tiết hôm nay thế nào?",
        "what is 2+2?",
        "cho tôi biết thêm về học bổng đó"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        
        classification = classify_query(query)
        print(f"Type: {classification.query_type}")
        print(f"Reasoning: {classification.reasoning}")
        print(f"Use RAG: {should_use_rag(classification)}")
        
        if not should_use_rag(classification):
            response = get_direct_response(classification, query)
            print(f"Direct Response: {response}")
