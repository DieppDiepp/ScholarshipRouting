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

# --- ROUTER PROMPT (MULTILINGUAL) ---
router_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an intelligent multilingual query classifier for a study abroad scholarship chatbot.\n"
     "The user's query can be in ANY language (English, Vietnamese, Japanese, Korean, Chinese, etc.).\n"
     "Your task is to classify it into ONE of these categories:\n\n"
     
     "1. **greeting**: Simple greetings or introductions in any language\n"
     "2. **scholarship_search**: Questions about scholarships, studying abroad, funding, applications\n"
     "3. **chitchat**: Casual conversation, thanks, small talk (NOT scholarship related)\n"
     "4. **off_topic**: Questions unrelated to scholarships or education\n\n"
     
     "RULES:\n"
     "- ANY scholarship/study abroad keyword → 'scholarship_search'\n"
     "- Follow-ups like 'tell me more' → 'scholarship_search'\n"
     "- Only pure greetings/thanks get 'greeting'/'chitchat'"
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
    Hỗ trợ đa ngôn ngữ (không cần dịch trước).
    Tự động skip key hết quota và thử key tiếp theo.
    
    Args:
        user_query: Câu hỏi gốc của user (bất kỳ ngôn ngữ nào)
        
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
            
            # Invoke chain trực tiếp (không cần translate)
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

# --- DYNAMIC RESPONSE GENERATION (Multilingual) ---
response_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly study abroad scholarship advisor chatbot.\n"
     "Generate a SHORT, appropriate response based on the query type.\n\n"
     "Response templates:\n"
     "- greeting: Greet warmly, introduce yourself as scholarship advisor, ask what they need\n"
     "- chitchat: Thank them politely, remind you can help with scholarships\n"
     "- off_topic: Apologize politely, state you only help with scholarships, ask if they have scholarship questions\n\n"
     "CRITICAL: Respond in the SAME LANGUAGE as the user's original query.\n"
     "Keep it concise (2-3 sentences max). Use emoji if appropriate (👋😊🎓)."
    ),
    ("human", "Query type: {query_type}\nUser query: {user_query}\n\nGenerate response:")
])

def get_direct_response(classification: config.QueryClassification, user_query: str) -> str:
    """
    Sinh câu trả lời động bằng LLM (hỗ trợ mọi ngôn ngữ).
    
    Args:
        classification: Kết quả phân loại từ router
        user_query: Query gốc của user
        
    Returns:
        Câu trả lời bằng ngôn ngữ của user
    """
    from langchain_core.output_parsers import StrOutputParser
    from .llm_factory import get_translator_llm  # Dùng chung translator LLM (nhẹ)
    
    try:
        llm = get_translator_llm()  # Flash model, nhanh
        chain = response_prompt | llm | StrOutputParser()
        
        response = chain.invoke({
            "query_type": classification.query_type,
            "user_query": user_query
        })
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        # Fallback tiếng Anh nếu LLM fail
        return "Hello! I'm your scholarship advisor. How can I help you find scholarships?"

if __name__ == '__main__':
    # Test router với 50 queries để kiểm tra quota limits
    test_queries = [
        # Greetings (10)
        "xin chào bạn",
        "hello there",
        "hi",
        "chào buổi sáng",
        "good morning",
        "hey",
        "xin chào",
        "hello",
        "chào bạn",
        "こんにちは"
    ]
    
    print(f"\n🧪 TESTING ROUTER WITH {len(test_queries)} QUERIES")
    print(f"{'='*80}\n")
    
    # Tracking stats
    stats = {
        "greeting": 0,
        "scholarship_search": 0,
        "chitchat": 0,
        "off_topic": 0
    }
    quota_errors = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query}")
        
        try:
            classification = classify_query(query)
            stats[classification.query_type] += 1
            
            print(f"✅ Type: {classification.query_type}")
            print(f"   Reasoning: {classification.reasoning[:80]}...")
            
            if not should_use_rag(classification):
                response = get_direct_response(classification, query)
                print(f"   Direct Response: {response[:60]}...")
                
        except ResourceExhausted as e:
            print(f"❌ ALL KEYS EXHAUSTED at query #{i}")
            quota_errors.append(i)
            break
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:100]}")
            break
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total queries tested: {i}/{len(test_queries)}")
    print(f"\nClassification breakdown:")
    for query_type, count in stats.items():
        print(f"  - {query_type}: {count}")
    
    if quota_errors:
        print(f"\n⚠️ Quota errors at queries: {quota_errors}")
    else:
        print(f"\n✅ All queries completed successfully!")
