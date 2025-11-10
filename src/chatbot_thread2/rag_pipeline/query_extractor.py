from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from .. import config

# 1. Định nghĩa cấu trúc (Schema) mà chúng ta muốn LLM trích xuất
# Các tên trường (Country, Required_Degree) phải khớp 100%
# với các key trong metadata (File 4: structured_english_reports_master.json)
class ScholarshipSearchFilters(BaseModel):
    Country: Optional[str] = Field(
        None,
        description="Quốc gia mà người dùng muốn du học, trả về một hoặc nhiều tên quốc gia chính thức. Ví dụ: 'UK', 'USA', 'China', 'Hungary',... "
    )
    Scholarship_Type: Optional[str] = Field(
        None,
        description="Loại nguồn gốc học bổng người dùng muốn, chỉ chấp nhận trả về 1 hoặc nhiều các giá trị sau: 'Government, 'University', 'Organization/Foundation'"
    )
    Funding_Level: Optional[str] = Field(
        None,
        description="Mức tài trợ người dùng muốn, chỉ chấp nhận trả về 1 hoặc nhiều các giá trị sau: 'Full scholarship', 'Tuition Waiver', 'Stipend', 'Accommodation', 'Partial Funding', 'Fixed Amount', 'Other Costs'"
    )
    Required_Degree: Optional[str] = Field(
        None,
        description="Bằng tốt nghiệp cao nhất mà người dùng đang đề cập, chỉ chấp nhận trả về 1 trong các giá trị: 'High School Diploma','Bachelor', 'Master'"
    )
    Wanted_Degree:Optional[str] = Field(
        None,
        description="Bậc học mà người dùng muốn tìm, chỉ chấp nhận trả về 1 hoặc nhiều các giá trị sau:: 'Bachelor', 'Master', 'PhD'"
    )
    Eligible_Field_Group: Optional[str] = Field(
        None,
        description="Nhóm ngành học người dùng quan tâm, chỉ chấp nhận trả về 1 hoặc nhiều các giá trị sau: 'Education & Training', 'Arts, Design & Media', 'Humanities & Social Sciences', 'Economics & Business', 'Law & Public Policy', 'Natural Sciences', 'IT & Data Science', 'Engineering & Technology', 'Construction & Planning', 'Agriculture & Environment', 'Healthcare & Medicine', 'Social Services & Care', 'Personal Services & Tourism', 'Security & Defense', 'Library & Information Management', 'Transportation & Logistics'"
    )

# 2. Khởi tạo LLM (Gemini) - Đọc từ config
llm = ChatGoogleGenerativeAI(
    model=config.EXTRACTOR_LLM_MODEL,
    google_api_key=config.GOOGLE_API_KEY,
    temperature=config.EXTRACTOR_LLM_TEMP
)

# 3. Tạo một "Chain" có khả năng trích xuất theo cấu trúc (Structured Output)
structured_llm = llm.with_structured_output(ScholarshipSearchFilters)

# 4. Tạo Prompt - Cập nhật để phù hợp với schema mới
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Bạn là một chuyên gia trích xuất thông tin. "
     "Nhiệm vụ của bạn là trích xuất các tiêu chí tìm kiếm học bổng từ câu hỏi của người dùng. "
     "Chỉ trích xuất thông tin được cung cấp, không suy diễn hay thêm thông tin không có trong câu hỏi. "
     "Hãy tuân thủ tuyệt đối các giá trị được phép trong mô tả của từng trường."
     "Ví dụ: Nếu người dùng muốn 'học bổng toàn phần', hãy đặt Funding_Level là 'Full scholarship'. "
     "Nếu người dùng muốn học Thạc sĩ, hãy đặt Wanted_Degree là 'Master'. "
     "Nếu người dùng nói 'tôi vừa tốt nghiệp đại học', hãy đặt Required_Degree là 'Bachelor'."),
    ("human", "{user_query}")
])

# 5. Kết hợp Prompt và LLM
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
    print(f"Query 1: {filters1.model_dump_json(indent=2)}")
    
    query2 = "tôi muốn học bổng chính phủ hoặc của trường và vì tôi không có nhiều tài chính nên tôi muốn tìm học bổng toàn phần ngành khoa học máy tính"
    filters2 = extract_filters(query2)
    print(f"Query 2: {filters2.model_dump_json(indent=2)}")
    
    query3 = "có học bổng nào ở Thổ Nhĩ Kỳ không?"
    filters3 = extract_filters(query3)
    print(f"Query 3: {filters3.model_dump_json(indent=2)}")