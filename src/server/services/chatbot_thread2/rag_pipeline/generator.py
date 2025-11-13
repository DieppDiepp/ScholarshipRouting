from langchain_core.prompts import ChatPromptTemplate
# from langchain.docstore.document import Document
from langchain_core.documents import Document
from typing import List

# --- IMPORT MỚI ---
from .llm_factory import get_generator_llm
from ..config import ScholarshipAnswer # Import Schema từ config
from . import data_loader


# --- TẢI TOÀN BỘ VĂN BẢN (FILE 3) ---
# Tải File 3 (văn bản đầy đủ) MỘT LẦN khi load module
# Đây là DB chứa {tên_học_bổng: full_markdown_text}
print("Loading full text reports (File 3) for Generator context...")
FULL_TEXT_REPORTS = data_loader.load_text_reports()
print("Full text reports loaded.")


# 3. Hàm helper để "làm phẳng" context (THAY ĐỔI LỚN)
def format_context(docs: List[Document]) -> str:
    """
    Chuyển List[Document] (là các CHUNKS) thành một chuỗi (string)
    bằng cách tra cứu VĂN BẢN ĐẦY ĐỦ của chúng.
    """
    if not docs:
        return "Không tìm thấy học bổng nào phù hợp."
    
    formatted_string = ""
    # 'docs' là danh sách các CHUNK đã được lọc duy nhất
    for i, chunk_doc in enumerate(docs): 
        
        # Lấy tên HB từ metadata của chunk
        name = chunk_doc.metadata.get('Scholarship_Name')
        
        if not name:
            continue # Bỏ qua nếu chunk không có tên (hiếm khi)
            
        # --- ĐÂY LÀ NÂNG CẤP ---
        # Lấy NỘI DUNG ĐẦY ĐỦ (full text) từ DB đã load
        full_text = FULL_TEXT_REPORTS.get(name)
        
        if not full_text:
            # Nếu không tìm thấy, dùng tạm page_content của chunk
            full_text = chunk_doc.page_content
        
        formatted_string += f"--- Bối cảnh Học bổng {i+1} ---\n"
        formatted_string += f"Tên học bổng (Scholarship_Name): {name}\n"
        # Truyền toàn bộ nội dung markdown cho LLM
        formatted_string += f"Nội dung đầy đủ:\n{full_text}\n\n"
        
    return formatted_string

# 4. Tạo RAG Prompt (Cập nhật System Prompt)
system_prompt_template = """
Bạn là một trợ lý AI tư vấn du học chuyên nghiệp và thân thiện.
Nhiệm vụ của bạn là tổng hợp thông tin từ BỐI CẢNH (CONTEXT) được cung cấp để trả lời câu hỏi của người dùng.
BỐI CẢNH chứa NỘI DUNG ĐẦY ĐỦ của các học bổng (bằng tiếng Anh).

--- QUY TẮC TRẢ LỜI (RẤT QUAN TRỌNG) ---
1.  **QUY TẮC NGÔN NGỮ:** Bạn PHẢI trả lời bằng ngôn ngữ mà người dùng đã sử dụng trong "CÂU HỎI GỐC CỦA NGƯỜI DÙNG".
    * Ví dụ: Nếu câu hỏi gốc là tiếng Việt, trả lời bằng tiếng Việt.
    * Ví dụ: Nếu câu hỏi gốc là tiếng Anh, trả lời bằng tiếng Anh.
2.  Chỉ sử dụng thông tin từ BỐI CẢNH. Không bịa đặt thông tin.
3.  Tên học bổng phải được lấy CHÍNH XÁC từ 'Scholarship_Name' trong context.
4.  Khi trả lời, hãy tóm tắt ngắn gọn tại sao các học bổng này phù hợp.
5.  Cố gắng tìm các thông tin quan trọng như HẠN NỘP ĐƠN (DEADLINE) hoặc YÊU CẦU (REQUIREMENTS) và đề cập nếu nó quan trọng.

--- CÂU HỎI GỐC CỦA NGƯỜI DÙNG (Để phát hiện ngôn ngữ) ---
{original_user_query}

--- BỐI CẢNH (CONTEXT) ---
{context}
--- KẾT THÚC BỐI CẢNH ---
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_template),
    ("human", "Hãy trả lời dựa trên câu hỏi gốc của tôi.") 
    # Human prompt ở đây không còn quan trọng bằng context và câu hỏi gốc
])


def generate_answer(original_user_query: str, retrieved_docs: List[Document]) -> ScholarshipAnswer:
    """
    Hàm chính: Nhận query gốc (để biết ngôn ngữ) và context.
    """
    if not retrieved_docs:
        print("--- No relevant documents found. Returning default answer. ---")
        return ScholarshipAnswer(
            scholarship_names=[],
            answer="Rất tiếc, mình không tìm thấy học bổng nào khớp chính xác với tất cả các tiêu chí của bạn. Bạn có muốn thử tìm kiếm với ít bộ lọc hơn không?"
        )
    
    # 1. Định dạng context (Hàm này giữ nguyên)
    formatted_context = format_context(retrieved_docs)
    
    # 2. Gọi LLM
    print("--- Generating final answer (calling LLM) ---")
    
    # --- TẠO LLM VÀ CHAIN MỚI MỖI LẦN GỌI ---
    generator_llm = get_generator_llm() # Lấy LLM (đã gắn schema) với key xoay vòng
    generation_chain = prompt | generator_llm
    
    response_obj = generation_chain.invoke({
        "context": formatted_context,
        "original_user_query": original_user_query
    })
    
    return response_obj