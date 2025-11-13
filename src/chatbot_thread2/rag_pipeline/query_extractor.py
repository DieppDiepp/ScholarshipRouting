from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from .. import config
# --- IMPORT MỚI ---
from .llm_factory import get_extractor_llm
from ..config import ScholarshipSearchFilters # Import Schema từ config


# 4. Tạo Prompt - CẬP NHẬT (RẤT QUAN TRỌNG)
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Bạn là một chuyên gia trích xuất thông tin VÀ ÁNH XẠ (mapper) siêu chính xác. "
     "Nhiệm vụ của bạn là trích xuất các tiêu chí VÀ ÁNH XẠ chúng vào các giá trị được phép trong schema."
     "Hãy tuân thủ tuyệt đối các giá trị được phép VÀ ĐỊNH DẠNG (LIST[str] hoặc str). KHÔNG ĐƯỢC tự ý sáng tạo giá trị mới."
     
     "\n--- QUY TẮC ÁNH XẠ BẮT BUỘC (MAPPING RULES) ---"
     "BẠN PHẢI SỬ DỤNG CÁC GIÁ TRỊ CHÍNH TẢ CHÍNH XÁC SAU:"
     
     "1. Funding_Level:"
     "   - Nếu người dùng nói 'học bổng toàn phần', 'full funding', 'full ride': LUÔN TRẢ VỀ ['Full scholarship']"
     "   - Nếu người dùng nói 'miễn học phí': LUÔN TRẢ VỀ ['Tuition Waiver']"
     
     "2. Eligible_Field_Group:"
     "   - Nếu người dùng nói 'khoa học máy tính', 'IT', 'công nghệ thông tin', 'khoa học dữ liệu', 'data science': LUÔN TRẢ VỀ ['IT & Data Science']"
     "   - Nếu người dùng nói 'kỹ thuật', 'engineering': LUÔN TRẢ VỀ ['Engineering & Technology']"
     "   - Nếu người dùng nói 'kinh doanh', 'kinh tế', 'quản trị': LUÔN TRẢ VỀ ['Economics & Business']"
     "   - (Bạn tự suy luận các ngành khác vào các nhóm còn lại trong description)"

     "\n--- QUY TẮC ĐỊNH DẠNG (FORMAT RULES) ---"
     "1. VỚI CÁC TRƯỜNG LÀ DANH SÁCH (List[str]), LUÔN TRẢ VỀ 1 DANH SÁCH, ngay cả khi chỉ có 1 giá trị. (Ví dụ: Wanted_Degree: ['Master'])."
     "2. NẾU NGƯỜI DÙNG HỎI VỀ MỘT KHU VỰC (ví dụ: 'Châu Âu', 'Châu Á'), hãy suy luận và trả về một DANH SÁCH các quốc gia tiêu biểu."
     "   Ví dụ 'Châu Âu': ['France', 'Germany', 'UK', 'Italy', 'Spain', 'Netherlands', 'Sweden', 'Hungary', 'Switzerland', 'Belgium', 'Austria', 'Denmark', 'Finland', 'Norway', 'Poland', 'Portugal', 'Ireland', 'Czech Republic']"
     "   Ví dụ 'Đông Nam Á': ['Singapore', 'Thailand', 'Malaysia', 'Vietnam', 'Philippines', 'Indonesia']"),

    ("human", "{user_query}")
])


def extract_filters(user_query: str) -> ScholarshipSearchFilters:
    """
    Nhận query của người dùng và trả về đối tượng Pydantic chứa các bộ lọc.
    """
    print(f"--- Extracting filters from query: '{user_query}' ---")
    
    # --- TẠO LLM VÀ CHAIN MỚI MỖI LẦN GỌI ---
    extractor_llm = get_extractor_llm() # Lấy LLM (đã gắn schema) với key xoay vòng
    extractor_chain = prompt | extractor_llm
    
    return extractor_chain.invoke({"user_query": user_query})

if __name__ == '__main__':
    # Test thử
    query1 = "tôi muốn tìm hiểu về du học anh trình độ thạc sĩ"
    filters1 = extract_filters(query1)
    print(f"Query 1: {filters1.model_dump_json(indent=2, exclude_none=True)}")
    
    query2 = "tôi muốn học bổng chính phủ hoặc của trường và vì tôi không có nhiều tài chính nên tôi muốn tìm học bổng toàn phần ngành khoa học máy tính"
    filters2 = extract_filters(query2)
    print(f"Query 2: {filters2.model_dump_json(indent=2, exclude_none=True)}")
    
    query3 = "có học bổng nào ở Thổ Nhĩ Kỳ không?"
    filters3 = extract_filters(query3)
    print(f"Query 3: {filters3.model_dump_json(indent=2, exclude_none=True)}")

    query4 = "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu"
    filters4 = extract_filters(query4)
    print(f"Query 4: {filters4.model_dump_json(indent=2, exclude_none=True)}")