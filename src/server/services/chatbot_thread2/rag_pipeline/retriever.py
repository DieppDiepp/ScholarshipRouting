from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional

from .. import config
from .indexing import get_embedding_model, get_vector_store_path
from .query_extractor import ScholarshipSearchFilters, extract_filters
import logging

logger = logging.getLogger(__name__)


# 1. Bỏ việc load ở global scope. Đặt một biến toàn cục là None
# Bỏ: vector_store = load_vector_store()
GLOBAL_VECTOR_STORE: Optional[Chroma] = None

# 2. Đổi tên hàm
def _load_vector_store_once() -> Chroma:
    """
    Hàm này chỉ được gọi MỘT LẦN.
    Tải Vector Store và embedding model vào RAM.
    """
    # 3. Dùng biến toàn cục
    global GLOBAL_VECTOR_STORE
    
    # Nếu đã load rồi, không làm gì cả
    if GLOBAL_VECTOR_STORE is not None:
        return GLOBAL_VECTOR_STORE

    # Nếu chưa load (lần chạy đầu tiên)
    logger.info("--- LAZY LOADING: Bắt đầu tải Vector Store và Embedding Model... (Chỉ 1 lần) ---")
    
    embedding_function = get_embedding_model()
    vector_store_path = get_vector_store_path()
    
    logger.info(f"Loading Vector Store from: {vector_store_path}")
    logger.info(f"Using embedding model: {config.EMBEDDING_CHOICE}")
    
    GLOBAL_VECTOR_STORE = Chroma(
        persist_directory=vector_store_path,
        embedding_function=embedding_function,
        collection_name=config.COLLECTION_NAME
    )
    
    logger.info("--- LAZY LOADING: Tải Vector Store hoàn tất! ---")
    return GLOBAL_VECTOR_STORE

# 3. Tạo hàm "getter"
def get_vector_store() -> Chroma:
    """
    Hàm "getter" công khai. Nó sẽ gọi _load_vector_store_once()
    nếu cần, hoặc trả về store đã load.
    """
    # Dòng này đảm bảo store được load trước khi sử dụng
    return _load_vector_store_once()

WILDCARD_FIELDS = ["All fields"]

# (Hàm apply_post_retrieval_filters giữ nguyên)
def apply_post_retrieval_filters(docs: List[Document], filters: ScholarshipSearchFilters) -> List[Document]:
    filtered_docs = []
    filter_data = filters.model_dump(exclude_none=True)
    
    if not filter_data:
        return docs
        
    logger.info(f"--- Applying post-retrieval filters: {filter_data} ---")
    
    for doc in docs:
        matches_all_filters = True
        for key, value in filter_data.items():
            metadata_value = doc.metadata.get(key)
            if metadata_value is None:
                matches_all_filters = False
                break
            
            metadata_value_str = str(metadata_value).lower()
            
            if key == "Eligible_Field_Group":
                is_wildcard = False
                for wildcard in WILDCARD_FIELDS:
                    if wildcard in metadata_value_str:
                        is_wildcard = True
                        break
                
                if is_wildcard:
                    # Học bổng này dành cho mọi ngành -> Pass filter này ngay lập tức
                    continue

            if isinstance(value, list):
                any_match_in_list = False
                for item in value:
                    if str(item).lower() in metadata_value_str:
                        any_match_in_list = True
                        break
                if not any_match_in_list:
                    matches_all_filters = False
                    break
            else:
                if str(value).lower() not in metadata_value_str:
                    matches_all_filters = False
                    break
                
        if matches_all_filters:
            filtered_docs.append(doc)
            
    return filtered_docs

# (Hàm search_scholarships SỬA 1 DÒNG)
def search_scholarships(user_query: str, 
                        filters: ScholarshipSearchFilters, 
                        initial_k: int = config.INITIAL_K_RETRIEVAL, 
                        final_k: int = config.FINAL_K_RETRIEVAL) -> List[Document]:
    
    vector_store = get_vector_store()
    
    # Bước 1: Semantic Search (Không dùng filter)
    logger.info(f"--- Step 1: Semantic Search (k={initial_k}) ---")
    initial_results = vector_store.similarity_search_with_score(
        query=user_query,
        k=initial_k
    )
    initial_docs = [doc for doc, score in initial_results]
    
    # Bước 2: Post-retrieval Filtering
    logger.info("--- Step 2: Post-retrieval Filtering ---")
    filtered_docs = apply_post_retrieval_filters(initial_docs, filters)
    
    # --- BƯỚC 3: LỌC TRÙNG LẶP ---
    logger.info(f"--- Step 3: De-duplicating results (by Scholarship_Name) ---")
    unique_scholarships = set()
    final_unique_docs = []
    
    for doc in filtered_docs:
        scholarship_name = doc.metadata.get('Scholarship_Name')
        
        if scholarship_name and scholarship_name not in unique_scholarships:
            final_unique_docs.append(doc)
            unique_scholarships.add(scholarship_name)
        
        if len(final_unique_docs) >= final_k:
            break
            
    logger.info(f"--- Found {len(final_unique_docs)} unique scholarship chunks (after filtering & de-duping) ---")
    
    return final_unique_docs

if __name__ == '__main__':
    
    logger.info(f"Testing RAG pipeline with '{config.EMBEDDING_CHOICE}' model.")
    
    test_query = "Tôi muốn tìm học bổng toàn phần thạc sĩ ở Trung Quốc"
    
    extracted_filters = extract_filters(test_query)
    logger.info(f"Extracted filters: {extracted_filters.model_dump_json(indent=2, exclude_none=True)}")
    
    retrieved_docs = search_scholarships(test_query, extracted_filters)
    
    for i, doc in enumerate(retrieved_docs):
        logger.info(f"\n--- Document {i+1} ---")
        logger.info(f"Source: {doc.metadata.get('Scholarship_Name')}")
        logger.info(f"Country: {doc.metadata.get('Country')}")
        logger.info(f"Funding: {doc.metadata.get('Funding_Level')}")
        logger.info(f"Text Chunk: {doc.page_content[:300]}...")