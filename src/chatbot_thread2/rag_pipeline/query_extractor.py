from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from .. import config

# 1. Định nghĩa cấu trúc (Schema)
# (Mình đã sửa 1 lỗi chính tả nhỏ: "LIST)1" -> "LIST) 1")
class ScholarshipSearchFilters(BaseModel):
    Country: Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Quốc gia mà người dùng muốn du học. Luôn trả về một DANH SÁCH (LIST) 1 hoặc nhiều tên quốc gia chính thức. Ví dụ: ['UK'], ['USA', 'Canada'], ['China'], ['Hungary']"
    )
    Scholarship_Type: Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Loại nguồn gốc học bổng. Luôn trả về DANH SÁCH (LIST) 1 hoặc nhiều giá trị sau: ['Government'], ['University'], ['Organization/Foundation']"
    )
    Funding_Level: Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Mức tài trợ. Luôn trả về DANH SÁCH (LIST) 1 hoặc nhiều giá trị sau: ['Full scholarship'], ['Tuition Waiver'], ['Stipend'], ['Accommodation'], ['Partial Funding'], ['Fixed Amount'], ['Other Costs']"
    )
    Required_Degree: Optional[str] = Field( # <-- GIỮ NGUYÊN (vì là '1 trong')
        None,
        description="Bằng tốt nghiệp cao nhất mà người dùng đang đề cập, chỉ chấp nhận trả về 1 TRONG các giá trị: 'High School Diploma','Bachelor', 'Master'"
    )
    Wanted_Degree:Optional[List[str]] = Field( # <-- ĐỔI SANG List[str]
        None,
        description="Bậc học mà người dùng muốn tìm. Luôn trả về DANH SÁCH 1 hoặc nhiều giá trị sau: ['Bachelor'], ['Master'], ['PhD']"
    )
    Eligible_Field_Group: Optional[List[str]] = Field(
        None,
        description="Nhóm ngành học người dùng quan tâm, Luôn trả về DANH SÁCH 1 hoặc nhiều giá trị, ví dụ: ['IT & Data Science'], ['Engineering & Technology', 'Natural Sciences']. DANH SÁCH CHỈ CÓ THỂ BAO GỒM CÁC GIÁ TRỊ: 'Education & Training', 'Arts, Design & Media', 'Humanities & Social Sciences', 'Economics & Business', 'Law & Public Policy', 'Natural Sciences', 'IT & Data Science', 'Engineering & Technology', 'Construction & Planning', 'Agriculture & Environment', 'Healthcare & Medicine', 'Social Services & Care', 'Personal Services & Tourism', 'Security & Defense', 'Library & Information Management', 'Transportation & Logistics', 'All fields'"
    )

# 2. Khởi tạo LLM (Giữ nguyên)
llm = ChatGoogleGenerativeAI(
    model=config.EXTRACTOR_LLM_MODEL,
    google_api_key=config.GOOGLE_API_KEY,
    temperature=config.EXTRACTOR_LLM_TEMP
)

# 3. Tạo "Chain" (Giữ nguyên)
structured_llm = llm.with_structured_output(ScholarshipSearchFilters)

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

# 5. Kết hợp Prompt và LLM (Giữ nguyên)
extractor_chain = prompt | structured_llm

def extract_filters(user_query: str) -> ScholarshipSearchFilters:
    """
    Nhận query của người dùng và trả về đối tượng Pydantic chứa các bộ lọc.
    """
    print(f"--- Extracting filters from query: '{user_query}' ---")
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