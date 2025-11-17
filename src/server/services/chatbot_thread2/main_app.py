import warnings
import logging # <-- THÊM IMPORT
from services.auth_svc import get_profile

# Lấy logger cho file này (dòng này giữ nguyên)
logger = logging.getLogger(__name__)

from .rag_pipeline.translator import translate_query_to_english # (MỚI)
from .rag_pipeline.query_extractor import extract_filters
from .rag_pipeline.retriever import search_scholarships
from .rag_pipeline.generator import generate_answer

# --- Hàm helper để format lịch sử ---
def format_chat_history(user_id: str, limit: int = 6) -> str:
    """
    Lấy lịch sử chat từ Firestore và format thành chuỗi string.
    Chỉ lấy 'limit' tin nhắn gần nhất để tiết kiệm token.
    """
    if not user_id:
        return "No history available."

    try:
        # Gọi hàm get_profile của bạn
        user_profile = get_profile(user_id)
        
        if not user_profile:
            return "No history available."
        
        # Giả sử field lưu lịch sử tên là 'chat_history'
        # Bạn hãy đổi tên key này nếu trong DB bạn lưu tên khác (ví dụ: 'messages', 'history'...)
        history_list = user_profile.get("chat_history", [])
        
        if not history_list:
            return "No history available."

        # Lấy n tin nhắn cuối cùng
        recent_history = history_list[-limit:]
        
        formatted_str = ""
        for msg in recent_history:
            role = msg.get("role", "unknown") # user hoặc model/assistant
            content = msg.get("content", "")
            # Chuẩn hóa role để LLM dễ hiểu
            if role == "user":
                formatted_str += f"User: {content}\n"
            else:
                formatted_str += f"AI: {content}\n"
                
        return formatted_str

    except Exception as e:
        logger.error(f"Error fetching chat history for user {user_id}: {e}")
        return "Error fetching history."
    
# --- Cập nhật hàm ask_chatbot ---
def ask_chatbot(query: str, user_id: str = None):
    """
    Chạy pipeline RAG có tích hợp lịch sử chat.
    """
    logger.info(f"========= Query Mới =========\nUser ID: {user_id}\nQuery Gốc: {query}\n")
    
    # 1. Lấy và format lịch sử chat (MỚI)
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