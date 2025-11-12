from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .. import config

# Khởi tạo LLM dịch thuật
translator_llm = ChatGoogleGenerativeAI(
    model=config.TRANSLATOR_LLM_MODEL,
    google_api_key=config.GOOGLE_API_KEY,
    temperature=config.TRANSLATOR_LLM_TEMP
)

# Prompt để dịch
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert translator. Your task is to translate the user's query into English. "
     "Translate the content retain the full meaning, including specific details like 'high GPA' or 'leadership skills'. "
     "Only output the translated English text and nothing else."),
    ("human", "{user_query}")
])

output_parser = StrOutputParser()

# Chain dịch thuật
translation_chain = translate_prompt | translator_llm | output_parser

def translate_query_to_english(user_query: str) -> str:
    """
    Dịch query của người dùng sang tiếng Anh để tối ưu RAG.
    """
    print(f"--- Translating query: '{user_query}' ---")
    
    # Kiểm tra xem query đã là tiếng Anh chưa
    # (Đây là một phỏng đoán đơn giản, có thể cải thiện sau)
    if all(ord(c) < 128 for c in user_query):
        print("Query already in English. Skipping translation.")
        return user_query
        
    translated_query = translation_chain.invoke({"user_query": user_query})
    print(f"Translated query: '{translated_query}'")
    return translated_query

if __name__ == '__main__':
    # Test
    vi_query = "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu, tôi có gpa cao"
    en_query = translate_query_to_english(vi_query)
    print(f"Original: {vi_query}\nTranslated: {en_query}")
    
    en_query_test = "I have a high GPA"
    en_query_2 = translate_query_to_english(en_query_test)
    print(f"Original: {en_query_test}\nTranslated: {en_query_2}")