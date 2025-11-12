import warnings
from .rag_pipeline.translator import translate_query_to_english # (MỚI)
from .rag_pipeline.query_extractor import extract_filters
from .rag_pipeline.retriever import search_scholarships
from .rag_pipeline.generator import generate_answer

def ask_chatbot(query: str):
    """
    Chạy toàn bộ pipeline RAG: Translate -> Extract -> Retrieve -> Generate
    """
    print(f"========= Query Mới =========\nQuery Gốc: {query}\n")
    
    # --- (MỚI) PHASE 1: TRANSLATE ---
    # 1. Dịch query sang tiếng Anh để "bình thường hóa"
    english_query = translate_query_to_english(query)
    
    # --- PHASE 2: EXTRACT ---
    # 2. Bóc tách query (từ tiếng Anh) thành bộ lọc
    filters = extract_filters(english_query)
    print(f"\n[PHASE 2] Extracted Filters:\n{filters.model_dump_json(indent=2, exclude_none=True)}")
    
    # --- PHASE 3: RETRIEVE ---
    # 3. Lấy tài liệu (Dùng query tiếng Anh)
    retrieved_docs = search_scholarships(english_query, filters)
    
    # --- PHASE 4: GENERATE ---
    # 4. Tổng hợp câu trả lời (Dùng query GỐC để biết ngôn ngữ)
    final_answer_obj = generate_answer(query, retrieved_docs)
    
    # --- KẾT QUẢ ---
    print("\n--- 🤖 Chatbot Trả lời ---")
    print(final_answer_obj.answer)
    
    print("\n--- 🔑 Tên học bổng (Output cho ElasticSearch) ---")
    print(final_answer_obj.scholarship_names)
    
    print("\n===============================")

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    
    # --- Test Case 1 (Tiếng Việt) ---
    query1 = "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu, tôi có gpa cao và kỹ năng lãnh đạo tốt"
    ask_chatbot(query1)
    
    # --- Test Case 2 (Tiếng Anh) ---
    query2 = "I want to find a full scholarship for a Master’s program in Data Science in Europe. I have a high GPA and strong leadership skills."
    ask_chatbot(query2)