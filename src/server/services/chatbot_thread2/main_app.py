import warnings
import logging # <-- THÊM IMPORT

# Lấy logger cho file này (dòng này giữ nguyên)
logger = logging.getLogger(__name__)

from .rag_pipeline.translator import translate_query_to_english # (MỚI)
from .rag_pipeline.query_extractor import extract_filters
from .rag_pipeline.retriever import search_scholarships
from .rag_pipeline.generator import generate_answer

def ask_chatbot(query: str):
    """
    Chạy toàn bộ pipeline RAG: Translate -> Extract -> Retrieve -> Generate
    Returns: final_answer_obj từ generate_answer
    """
    # Thay print() bằng logger.info()
    logger.info(f"========= Query Mới =========\nQuery Gốc: {query}\n")
    
    # --- (MỚI) PHASE 1: TRANSLATE ---
    english_query = translate_query_to_english(query)
    
    # --- PHASE 2: EXTRACT ---
    filters = extract_filters(english_query)
    # Thay print() bằng logger.info()
    logger.info(f"\n[PHASE 2] Extracted Filters:\n{filters.model_dump_json(indent=2, exclude_none=True)}")
    
    # --- PHASE 3: RETRIEVE ---
    retrieved_docs = search_scholarships(english_query, filters)
    
    # --- PHASE 4: GENERATE ---
    final_answer_obj = generate_answer(query, retrieved_docs)
    
    # --- KẾT QUẢ (THAY PRINT BẰNG LOGGER) ---
    logger.info("\n--- 🤖 Chatbot Trả lời ---")
    logger.info(final_answer_obj.answer)
    
    logger.info("\n--- 🔑 Tên học bổng (Output cho ElasticSearch) ---")
    # Thêm f-string để đảm bảo list được in ra
    logger.info(f"{final_answer_obj.scholarship_names}") 
    
    logger.info("\n===============================")
    
    # Trả về kết quả
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