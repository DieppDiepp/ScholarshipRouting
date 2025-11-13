import os
import shutil
from tqdm import tqdm
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.base import Embeddings # Dùng class base
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from .custom_embeddings import CustomVietnameseEmbeddings
from .llm_factory import get_next_api_key
from . import data_loader
from .. import config
from typing import List, Union # Mới

def create_documents() -> List[Document]:
    """
    Kết hợp File 3 (văn bản) và File 4 (metadata) để tạo
    danh sách các Document LangChain.
    """
    # 1. Tải metadata (File 4)
    metadata_map = data_loader.load_structured_metadata()
    
    # 2. Tải văn bản (File 3)
    text_reports = data_loader.load_text_reports()
    
    all_docs = []
    
    print("Combining text reports with metadata...")
    # Dùng tqdm để xem tiến độ
    for name, content in tqdm(text_reports.items()):
        # 3. Lấy metadata tương ứng
        metadata = metadata_map.get(name)
        
        if not metadata:
            print(f"Warning: No metadata found for '{name}'. Skipping.")
            continue

        # Thêm lại 'Scholarship_Name' vào trong metadata
        # để chúng ta có thể truy cập nó sau này.
        metadata['Scholarship_Name'] = name
            
        # 4. Tạo 1 Document LangChain
        # page_content là nội dung văn bản (từ File 3)
        # metadata là toàn bộ thông tin cấu trúc (từ File 4)
        doc = Document(page_content=content, metadata=metadata)
        all_docs.append(doc)
        
    return all_docs

def split_documents(documents: List[Document]) -> List[Document]:
    """
    Cắt các Document lớn thành các chunks nhỏ hơn.
    Chúng ta sẽ dùng 2 lớp splitter:
    1. MarkdownHeaderTextSplitter: Cắt theo các tiêu đề Markdown (##, ###)
    2. RecursiveCharacterTextSplitter: Cắt nhỏ các đoạn còn lại
    """
    print("Splitting documents into chunks...")
    
    # Cấu hình splitter theo Markdown (##, ###)
    # File text_reports_master.json của bạn dùng định dạng này
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, 
        strip_headers=False
    )
    
    # Splitter dự phòng để cắt các đoạn quá lớn
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

    all_chunks = []
    
    for doc in tqdm(documents):
        # Thử cắt bằng Markdown splitter trước
        chunks_md = markdown_splitter.split_text(doc.page_content)
        
        final_chunks_for_doc = []
        for chunk in chunks_md:
            # Metadata từ document gốc (File 4) sẽ được copy vào chunk
            # và metadata của header (ví dụ: "Header 2": "3. Funding and Benefits") 
            # cũng được thêm vào
            chunk.metadata.update(doc.metadata)
            
            # Kiểm tra xem chunk này có quá lớn không
            if len(chunk.page_content) > config.CHUNK_SIZE:
                # Nếu quá lớn, dùng RecursiveSplitter để cắt nhỏ
                sub_chunks = recursive_splitter.create_documents(
                    [chunk.page_content],
                    metadatas=[chunk.metadata] # Truyền metadata xuống
                )
                final_chunks_for_doc.extend(sub_chunks)
            else:
                final_chunks_for_doc.append(chunk)
        
        all_chunks.extend(final_chunks_for_doc)
        
    print(f"Split {len(documents)} documents into {len(all_chunks)} chunks.")
    return all_chunks

def get_embedding_model() -> Embeddings:
    """
    Đọc config và khởi tạo model embedding tương ứng.
    """
    choice = config.EMBEDDING_CHOICE
    
    if choice == "google":
        print(f"Initializing Google embedding model: {config.GOOGLE_EMBEDDING_MODEL_NAME}")
        
        # --- SỬA LỖI ---
        # Lấy MỘT key từ pool để khởi tạo embedding
        # Thay vì: google_api_key=config.GOOGLE_API_KEY
        api_key = get_next_api_key() 
        return GoogleGenerativeAIEmbeddings(
            model=config.GOOGLE_EMBEDDING_MODEL_NAME,
            google_api_key=api_key # <-- Dùng key vừa lấy từ factory
        )
    elif choice == "hf":
        print(f"Initializing CustomVietnameseEmbeddings: {config.HF_EMBEDDING_MODEL_NAME}")
        return CustomVietnameseEmbeddings(
            model_name=config.HF_EMBEDDING_MODEL_NAME,
            max_length=config.HF_EMBEDDING_MAX_LENGTH
        )
    else:
        raise ValueError(f"Invalid EMBEDDING_CHOICE: '{choice}'. Must be 'google' or 'hf'.")

# --- Hàm mới: Lấy đường dẫn lưu VDB ---
def get_vector_store_path() -> str:
    """
    Đọc config và trả về đường dẫn thư mục VDB tương ứng.
    """
    choice = config.EMBEDDING_CHOICE
    
    if choice == "google":
        return config.GOOGLE_VECTOR_STORE_DIR
    elif choice == "hf":
        return config.HF_VECTOR_STORE_DIR
    else:
        raise ValueError(f"Invalid EMBEDDING_CHOICE: '{choice}'.")


def build_vector_store():
    """
    Hàm chính: Tải, chunk, và index dữ liệu dựa trên
    model embedding được chọn trong config.
    """
    vector_store_path = get_vector_store_path()
    
    # Xóa Vector Store cũ nếu có
    if os.path.exists(vector_store_path):
        print(f"Removing old vector store at {vector_store_path}")
        shutil.rmtree(vector_store_path)
        
    # 1. Tạo Documents (kết hợp File 3 + File 4)
    documents = create_documents()
    
    # 2. Cắt thành chunks
    chunks = split_documents(documents)
    
    # 3. Khởi tạo model embedding (dựa trên config)
    embeddings = get_embedding_model()
    
    # 4. Index vào ChromaDB (lưu vào đúng thư mục)
    print(f"Building and persisting vector store for '{config.EMBEDDING_CHOICE}' model...")
    print(f"Store location: {vector_store_path}")
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=vector_store_path, # Dùng đường dẫn động
        collection_name=config.COLLECTION_NAME
    )
    
    print("--- Indexing Complete! ---")
    print(f"Total chunks indexed: {len(chunks)}")
    print(f"Vector store location: {vector_store_path}")

if __name__ == "__main__":
    # python -m src.chatbot_thread2.rag_pipeline.indexing
    build_vector_store()