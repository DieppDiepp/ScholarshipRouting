from langchain_chroma import Chroma
from langchain.docstore.document import Document
from typing import List, Dict, Any, Optional

from .. import config
# Import 2 hàm factory từ file indexing.py
from .indexing import get_embedding_model, get_vector_store_path
from .query_extractor import ScholarshipSearchFilters, extract_filters

# 1. Hàm tải Vector Store (Giữ nguyên)
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

# 2. HÀM MỚI: Lọc kết quả bằng Python
def apply_post_retrieval_filters(docs: List[Document], filters: ScholarshipSearchFilters) -> List[Document]:
    """
    Lọc danh sách các Document (đã truy vấn)
    dựa trên các tiêu chí (filters).
    """
    filtered_docs = []
    filter_data = filters.model_dump(exclude_none=True) # Chỉ lấy các filter có giá trị
    
    if not filter_data:
        # Nếu không có filter nào, trả về danh sách gốc
        return docs
        
    print(f"--- Applying post-retrieval filters: {filter_data} ---")
    
    for doc in docs:
        matches_all = True
        
        for key, value in filter_data.items():
            # Lấy giá trị metadata từ document
            metadata_value = doc.metadata.get(key)
            
            if metadata_value is None:
                # Nếu metadata không có trường này, loại
                matches_all = False
                break
                
            # So sánh linh hoạt (không phân biệt hoa thường, chứa)
            if str(value).lower() not in str(metadata_value).lower():
                matches_all = False
                break
                
        if matches_all:
            filtered_docs.append(doc)
            
    return filtered_docs

# 3. HÀM CHÍNH (Sửa lại): Tìm kiếm 2 bước
def search_scholarships(user_query: str, 
                        filters: ScholarshipSearchFilters, 
                        initial_k: int = 25, 
                        final_k: int = 5) -> List[Document]:
    """
    Thực hiện tìm kiếm 3 bước:
    1. Semantic Search (lấy initial_k)
    2. Post-retrieval Filtering (lọc bằng Python)
    3. De-duplication (lọc trùng lặp)
    4. Trả về top final_k
    """
    
    # Bước 1: Semantic Search (Không dùng filter)
    print(f"--- Step 1: Semantic Search (k={initial_k}) ---")
    initial_results = vector_store.similarity_search_with_score(
        query=user_query,
        k=initial_k
    )
    initial_docs = [doc for doc, score in initial_results]
    
    # Bước 2: Post-retrieval Filtering
    print("--- Step 2: Post-retrieval Filtering ---")
    filtered_docs = apply_post_retrieval_filters(initial_docs, filters)
    
    # --- BƯỚC 3 MỚI: LỌC TRÙNG LẶP ---
    print(f"--- Step 3: De-duplicating results (by Scholarship_Name) ---")
    unique_scholarships = set()
    final_unique_docs = []
    
    for doc in filtered_docs:
        # Lấy tên học bổng (lần này sẽ không bị None)
        scholarship_name = doc.metadata.get('Scholarship_Name')
        
        if scholarship_name and scholarship_name not in unique_scholarships:
            final_unique_docs.append(doc)
            unique_scholarships.add(scholarship_name)
        
        # Dừng lại khi đủ số lượng mong muốn
        if len(final_unique_docs) >= final_k:
            break
            
    print(f"--- Found {len(final_unique_docs)} unique scholarship chunks (after filtering & de-duping) ---")
    
    # Trả về các document đã lọc
    return final_unique_docs

if __name__ == '__main__':
    # Test toàn bộ luồng (Extractor + Retriever)
    
    print(f"Testing RAG pipeline with '{config.EMBEDDING_CHOICE}' model.")
    
    test_query = "Tôi muốn tìm học bổng toàn phần thạc sĩ ở Trung Quốc"
    
    # 1. Chạy extractor
    extracted_filters = extract_filters(test_query)
    print(f"Extracted filters: {extracted_filters.model_dump_json(indent=2, exclude_none=True)}")
    
    # 2. Chạy retriever
    retrieved_docs = search_scholarships(test_query, extracted_filters)
    
    # 3. In kết quả
    for i, doc in enumerate(retrieved_docs):
        print(f"\n--- Document {i+1} ---")
        print(f"Source: {doc.metadata.get('Scholarship_Name')}")
        print(f"Country: {doc.metadata.get('Country')}")
        print(f"Degree (Wanted): {doc.metadata.get('Wanted_Degree')}") # Sẽ không có
        print(f"Degree (Required): {doc.metadata.get('Required_Degree')}")
        print(f"Funding: {doc.metadata.get('Funding_Level')}")
        print(f"Text Chunk: {doc.page_content[:300]}...")