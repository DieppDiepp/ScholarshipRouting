import warnings
import logging
from services.auth_svc import get_profile

# Lấy logger cho file này
logger = logging.getLogger(__name__)

from .rag_pipeline.translator import translate_query_to_english
from .rag_pipeline.query_extractor import extract_filters
from .rag_pipeline.retriever import search_scholarships
from .rag_pipeline.generator import generate_answer
# --- IMPORT MỚI: QUERY ROUTER ---
from .rag_pipeline.query_router import classify_query, should_use_rag, get_direct_response
from . import config

# --- Hàm helper để format lịch sử ---
def format_chat_history(user_id: str, limit: int = 6) -> str:
    """
    Lấy lịch sử chat từ Firestore và format thành chuỗi string.
    Khớp với cấu trúc dữ liệu trong crm_svc: 
    Key: 'chatHistory'
    Item: { 'query': '...', 'answer': '...', 'timestamp': ... }
    """
    if not user_id:
        return "No history available."

    try:
        user_profile = get_profile(user_id)
        
        if not user_profile:
            return "No history available."
        
        history_list = user_profile.get("chatHistory", [])
        
        if not history_list:
            return "No history available."

        # Lấy n tin nhắn cuối cùng
        # Lưu ý: logic lưu là append, nên tin mới nhất ở cuối list.
        recent_history = history_list[-limit:]
        
        formatted_str = ""
        for chat_item in recent_history:
            user_text = chat_item.get("query", "")
            ai_text = chat_item.get("answer", "")
            
            if user_text:
                formatted_str += f"User: {user_text}\n"
            if ai_text:
                formatted_str += f"AI: {ai_text}\n"
        
        # Log ra để debug xem đã lấy được chưa
        logger.info(f"Formatted {len(recent_history)} history items for user {user_id}")
        
        return formatted_str

    except Exception as e:
        logger.error(f"Error fetching chat history for user {user_id}: {e}")
        return "Error fetching history."
    
# --- Cập nhật hàm ask_chatbot ---
def ask_chatbot(query: str, user_id: str = None):
    """
    Chạy pipeline RAG có tích hợp lịch sử chat VÀ QUERY ROUTER.
    
    Flow:
    1. Router phân loại query
    2. Nếu là greeting/chitchat/off_topic → Trả lời trực tiếp (NHANH)
    3. Nếu là scholarship_search → Chạy full RAG pipeline
    """
    logger.info(f"========= Query Mới =========\nUser ID: {user_id}\nQuery Gốc: {query}\n")
    
    # --- BƯỚC 0: QUERY ROUTING (MỚI) ---
    logger.info("[PHASE 0] Query Classification & Routing")
    classification = classify_query(query)
    
    # Nếu KHÔNG cần RAG → Trả lời trực tiếp
    if not should_use_rag(classification):
        logger.info(f"--- Query type '{classification.query_type}' không cần RAG. Trả lời trực tiếp. ---")
        direct_answer = get_direct_response(classification, query)
        
        # Trả về format giống ScholarshipAnswer để đồng nhất
        return config.ScholarshipAnswer(
            scholarship_names=[],
            answer=direct_answer
        )
    
    # --- NẾU CẦN RAG, CHẠY PIPELINE BÌNH THƯỜNG ---
    logger.info("--- Query cần RAG. Chạy full pipeline... ---")
    
    # 1. Lấy và format lịch sử chat
    chat_history_str = format_chat_history(user_id)
    logger.info(f"Chat History Context:\n{chat_history_str}")

    # 2. Translate
    english_query = translate_query_to_english(query)
    
    # 3. Extract
    filters = extract_filters(english_query)
    logger.info(f"\n[PHASE 2] Extracted Filters:\n{filters.model_dump_json(indent=2, exclude_none=True)}")
    
    # 4. Retrieve
    retrieved_docs = search_scholarships(english_query, filters)
    
    # 5. Generate (Truyền thêm history)
    final_answer_obj = generate_answer(query, retrieved_docs, chat_history_str)
    
    # --- KẾT QUẢ ---
    logger.info("\n--- 🤖 Chatbot Trả lời ---")
    logger.info(final_answer_obj.answer)
    logger.info("\n--- 🔑 Tên học bổng ---")
    logger.info(f"{final_answer_obj.scholarship_names}") 
    logger.info("\n===============================")
    
    # Trả về object để Route sử dụng
    return final_answer_obj

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    
    # --- Test Case 1 (Tiếng Việt) ---
    query1 = "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu, tôi có gpa cao và kỹ năng lãnh đạo tốt"
    ask_chatbot(query1)
    
    # --- Test Case 2 (Tiếng Anh) ---
    query2 = "I want to find a full scholarship for a Master’s program in Data Science in Europe. I have a high GPA and strong leadership skills."
    ask_chatbot(query2)

    # --- (THÊM DÒNG NÀY) ---
    # Bảo bộ đệm xả log vào file trước khi script thoát.
    logging.shutdown()