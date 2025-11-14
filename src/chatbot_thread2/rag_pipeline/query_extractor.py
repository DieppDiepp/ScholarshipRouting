from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from .. import config
# --- IMPORT MỚI ---
from .llm_factory import get_extractor_llm
from ..config import ScholarshipSearchFilters # Import Schema từ config
import logging # Thêm logging

logger = logging.getLogger(__name__)

# 4. Tạo Prompt (Đã dịch sang tiếng Anh)
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert information extraction and hyper-accurate mapping specialist. "
     "Your task is to extract criteria from the user's query AND map them to the allowed values in the schema."
     "You MUST strictly adhere to the allowed values AND formats (LIST[str] or str) specified in the field descriptions. DO NOT invent new values."
     
     "\n--- MANDATORY MAPPING RULES ---"
     "You MUST use the following exact string values:"
     
     "1. Funding_Level:"
     "   - If the user query mentions 'full scholarship', 'full funding', or 'full ride': ALWAYS return ['Full scholarship']"
     "   - If the user query mentions 'tuition waiver': ALWAYS return ['Tuition Waiver']"
     
     "2. Eligible_Field_Group:"
     "   - If the user query mentions 'computer science', 'IT', 'information technology', 'data science': ALWAYS return ['IT & Data Science']"
     "   - If the user query mentions 'engineering': ALWAYS return ['Engineering & Technology']"
     "   - If the user query mentions 'business', 'economics', 'management': ALWAYS return ['Economics & Business']"
     "   - (You must infer other fields into the remaining groups provided in the schema description)"

     "\n--- FORMAT RULES ---"
     "1. For fields that are LIST[str], ALWAYS return a list, even if there is only one value. (e.g., Wanted_Degree: ['Master'])."
     "2. IF THE USER ASKS ABOUT A REGION (e.g., 'Europe', 'Asia'), infer and return a LIST of representative countries for that region in the 'Country' field."
     "   Example 'Europe': ['France', 'Germany', 'UK', 'Italy', 'Spain', 'Netherlands', 'Sweden', 'Hungary', 'Switzerland', 'Belgium', 'Austria', 'Denmark', 'Finland', 'Norway', 'Poland', 'Portugal', 'Ireland', 'Czech Republic']"
     "   Example 'Southeast Asia': ['Singapore', 'Thailand', 'Malaysia', 'Vietnam', 'Philippines', 'Indonesia']"),

    ("human", "{user_query}")
])


def extract_filters(user_query: str) -> ScholarshipSearchFilters:
    """
    Takes the user query (in English) and returns the Pydantic filter object.
    """
    logger.info(f"--- Extracting filters from query: '{user_query}' ---")
    
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