from langchain.vectorstores.chroma import Chroma
from langchain.docstore.document import Document
from typing import List, Dict, Any, Optional

from .. import config
# Import 2 hàm factory từ file indexing.py
from .indexing import get_embedding_model, get_vector_store_path
from .query_extractor import ScholarshipSearchFilters, extract_filters

# 1. Hàm tải Vector Store
def load_vector_store():
    """
    Tải Vector Store (ChromaDB) đã tồn tại và
    model embedding tương ứng (dựa trên config).
    """
    embedding_function = get_embedding_model()
    vector_store_path = get_vector_store_path()
    
    print(f"Loading Vector Store from: {vector_store_path}")
    print(f"Using embedding model: {config.EMBEDDING_CHOICE}")
    
    vector_store = Chroma(
        persist_directory=vector_store_path,
        embedding_function=embedding_function,
        collection_name=config.COLLECTION_NAME
    )
    return vector_store

# Khởi tạo VDB một lần khi load module
vector_store = load_vector_store()

# 2. Hàm xây dựng bộ lọc cho ChromaDB
def build_chroma_filter(filters: ScholarshipSearchFilters) -> Optional[Dict[str, Any]]:
    """
    Chuyển đổi đối tượng Pydantic filters thành 
    dictionary filter cho ChromaDB.
    """
    filter_dict = {}
    
    # Lấy các trường đã được trích xuất
    data = filters.model_dump()
    
    for key, value in data.items():
        if value: # Chỉ thêm vào filter nếu LLM trích xuất được
            # Chroma hỗ trợ $like (giống %LIKE% trong SQL)
            # để tìm kiếm linh hoạt hơn
            filter_dict[key] = {"$like": f"%{value}%"}
            
    if not filter_dict:
        return None
        
    # Nếu có nhiều hơn 1 điều kiện, dùng $and
    if len(filter_dict) > 1:
        return {"$and": [ {k: v} for k, v in filter_dict.items() ]}
    
    # Nếu chỉ có 1 điều kiện
    return filter_dict

# 3. Hàm tìm kiếm chính (Hybrid Search)
def search_scholarships(user_query: str, filters: ScholarshipSearchFilters, k: int = 5) -> List[Document]:
    """
    Thực hiện tìm kiếm RAG:
    1. Filter (lọc) bằng metadata (từ 'filters')
    2. Semantic Search (tìm kiếm) bằng 'user_query'
    """
    print("--- Building Chroma filter ---")
    chroma_filter = build_chroma_filter(filters)
    
    if chroma_filter:
        print(f"Filter created: {chroma_filter}")
    else:
        print("No filters extracted, performing pure semantic search.")

    # Đây chính là bước Hybrid RAG
    # Chúng ta tìm kiếm ngữ nghĩa (similarity_search)
    # VÀ áp dụng bộ lọc (filter) cùng lúc
    results = vector_store.similarity_search(
        query=user_query,
        k=k,
        filter=chroma_filter
    )
    
    print(f"--- Found {len(results)} relevant chunks ---")
    return results

if __name__ == '__main__':
    # Test toàn bộ luồng (Extractor + Retriever)
    
    # Đảm bảo config.EMBEDDING_CHOICE = "hf" (hoặc "google")
    # để nó load đúng vector store bạn muốn test
    print(f"Testing RAG pipeline with '{config.EMBEDDING_CHOICE}' model.")
    
    test_query = "tôi muốn tìm học bổng toàn phần thạc sĩ ở Anh ngành kỹ thuật"
    
    # 1. Chạy extractor
    extracted_filters = extract_filters(test_query)
    print(f"Extracted filters: {extracted_filters.model_dump_json(indent=2)}")
    
    # 2. Chạy retriever
    retrieved_docs = search_scholarships(test_query, extracted_filters)
    
    # 3. In kết quả
    for i, doc in enumerate(retrieved_docs):
        print(f"\n--- Document {i+1} (Score: {doc.metadata.get('_score', 'N/A')}) ---")
        print(f"Source: {doc.metadata.get('Scholarship_Name')}")
        print(f"Country: {doc.metadata.get('Country')}")
        print(f"Degree: {doc.metadata.get('Required_Degree')}")
        print(f"Funding: {doc.metadata.get('Funding_Level')}")
        print(f"Text Chunk: {doc.page_content[:300]}...")