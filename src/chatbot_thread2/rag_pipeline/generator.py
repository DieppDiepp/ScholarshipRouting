from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from typing import List
import logging # Thêm logging

# --- IMPORT MỚI ---
from .llm_factory import get_generator_llm
from ..config import ScholarshipAnswer # Import Schema từ config
from . import data_loader

logger = logging.getLogger(__name__)

# (Phần tải FULL_TEXT_REPORTS giữ nguyên)
# --- TẢI TOÀN BỘ VĂN BẢN (FILE 3) ---
# Tải File 3 (văn bản đầy đủ) MỘT LẦN khi load module
# Đây là DB chứa {tên_học_bổng: full_markdown_text}
logger.info("Loading full text reports (File 3) for Generator context...")
FULL_TEXT_REPORTS = data_loader.load_text_reports()
logger.info("Full text reports loaded.")


# 3. Hàm helper để "làm phẳng" context (THAY ĐỔI LỚN)
def format_context(docs: List[Document]) -> str:
    """
    Chuyển List[Document] (là các CHUNKS) thành một chuỗi (string)
    bằng cách tra cứu VĂN BẢN ĐẦY ĐỦ của chúng.
    """
    if not docs:
        return "No suitable scholarships found."
    
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
        
        # Dùng Tiếng Anh cho các tiêu đề context
        formatted_string += f"--- Context for Scholarship {i+1} ---\n"
        formatted_string += f"Scholarship_Name: {name}\n"
        formatted_string += f"Full Text Content:\n{full_text}\n\n"
        
    return formatted_string

# 4. Tạo RAG Prompt (Đã dịch sang tiếng Anh)
system_prompt_template = """
You are a professional and friendly study abroad advisor AI.
Your task is to synthesize the information from the provided CONTEXT to answer the user's question.
The CONTEXT contains the FULL TEXT of the scholarships (in English).

--- RESPONSE RULES (VERY IMPORTANT) ---
1.  **LANGUAGE RULE:** You MUST respond in the same language used by the user in the 'ORIGINAL USER QUERY'.
    * Example: If the original query is in Vietnamese, respond in Vietnamese.
    * Example: If the original query is in English, respond in English.
    * Example: If the original query is in Chinese, respond in Chinese.
2.  Use ONLY information from the CONTEXT. Do not invent information.
3.  Scholarship names must be extracted EXACTLY from 'Scholarship_Name' in the context.
4.  When responding (e.g., in Vietnamese 'mình' - 'bạn'), briefly summarize why the scholarships are relevant.
5.  Try to find key information like DEADLINES or REQUIREMENTS from the FULL TEXT and mention them if relevant.

--- ORIGINAL USER QUERY (For language detection) ---
{original_user_query}

--- CONTEXT ---
{context}
--- END CONTEXT ---
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_template),
    # Dịch human prompt
    ("human", "Please answer based on my original query and the provided context.") 
])

def generate_answer(original_user_query: str, retrieved_docs: List[Document]) -> ScholarshipAnswer:
    """
    Hàm chính: Nhận query gốc (để biết ngôn ngữ) và context.
    """
    if not retrieved_docs:
        logger.info("--- No relevant documents found. Returning default answer. ---")
        # Trả về câu trả lời mặc định, generator sẽ cố gắng dịch nó
        # (Chúng ta có thể cải thiện điều này sau bằng cách phát hiện ngôn ngữ)
        return ScholarshipAnswer(
            scholarship_names=[],
            answer="Unfortunately, I couldn't find any scholarships that exactly match all your criteria. Would you like to try searching with fewer filters?"
        )
    
    formatted_context = format_context(retrieved_docs)
    
    logger.info("--- Generating final answer (calling LLM) ---")
    
    generator_llm = get_generator_llm()
    generation_chain = prompt | generator_llm
    
    response_obj = generation_chain.invoke({
        "context": formatted_context,
        "original_user_query": original_user_query
    })
    
    return response_obj