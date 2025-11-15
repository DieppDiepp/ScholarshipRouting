"""
Tool 4: RAG Search - Tìm kiếm trên RAG Database (Web Content)
"""
import json
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.utils.api_key_manager import get_next_gemini_key

class RAGSearchTool:
    """Tool tìm kiếm trên RAG database (web content + URLs)"""
    
    def __init__(self, rag_path: str = None):
        """Khởi tạo RAG Search Tool"""
        # Cấu hình Gemini API với key rotation
        genai.configure(api_key=get_next_gemini_key())
        
        # Đường dẫn RAG database
        self.rag_path = rag_path or Config.RAG_DATABASE_PATH
        
        # Khởi tạo ChromaDB client
        self.client = chromadb.PersistentClient(
            path=Config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Tên collection cho RAG
        self.collection_name = "rag_documents"
        self.collection = None
        
        # Load RAG data
        self.rag_documents = []
    
    def load_rag_database(self) -> List[Dict[str, Any]]:
        """Load RAG database từ JSONL file"""
        documents = []
        try:
            with open(self.rag_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        doc = json.loads(line)
                        documents.append(doc)
            print(f"✓ Đã load {len(documents)} documents từ RAG database")
        except FileNotFoundError:
            print(f"✗ Không tìm thấy RAG database: {self.rag_path}")
        except Exception as e:
            print(f"✗ Lỗi khi load RAG database: {e}")
        
        return documents
    
    def create_embeddings(self, text: str) -> List[float]:
        """Tạo embedding vector từ text"""
        try:
            result = genai.embed_content(
                model=Config.EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"✗ Lỗi tạo embedding: {e}")
            return []
    
    def index_rag_documents(self):
        """Index RAG documents vào ChromaDB"""
        try:
            # Load documents
            self.rag_documents = self.load_rag_database()
            
            if not self.rag_documents:
                print("⚠ Không có documents để index")
                return
            
            # Xóa collection cũ nếu tồn tại
            try:
                self.client.delete_collection(name=self.collection_name)
            except:
                pass
            
            # Tạo collection mới
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Chuẩn bị dữ liệu
            documents = []
            metadatas = []
            ids = []
            
            for idx, doc in enumerate(self.rag_documents):
                # Content để index
                content = doc.get("content", "")
                scholarship_name = doc.get("scholarship_name", "")
                url = doc.get("url", "")
                
                # Tạo document text
                doc_text = f"Scholarship: {scholarship_name}\n\n{content}"
                documents.append(doc_text)
                
                # Metadata
                metadatas.append({
                    "scholarship_name": scholarship_name,
                    "url": url,
                    "content": content[:500]  # Lưu preview
                })
                
                # ID
                ids.append(f"rag_doc_{idx}")
            
            # Tạo embeddings
            print(f"Đang tạo embeddings cho {len(documents)} RAG documents...")
            embeddings = []
            for doc in documents:
                emb = self.create_embeddings(doc)
                if emb:
                    embeddings.append(emb)
                else:
                    # Nếu không tạo được embedding, dùng zero vector
                    embeddings.append([0.0] * 768)
            
            # Thêm vào collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✓ Đã index {len(documents)} RAG documents vào vector database")
            
        except Exception as e:
            print(f"✗ Lỗi khi index RAG documents: {e}")
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm trong RAG database
        
        Args:
            query: Câu hỏi của người dùng
            top_k: Số lượng kết quả (mặc định 3)
            
        Returns:
            List các documents phù hợp với URLs
        """
        if top_k is None:
            top_k = 3  # RAG search trả về ít hơn
        
        try:
            # Load collection nếu chưa load
            if self.collection is None:
                try:
                    self.collection = self.client.get_collection(name=self.collection_name)
                except:
                    print("⚠ RAG collection chưa được index")
                    return []
            
            # Tạo embedding cho query
            query_embedding = self.create_embeddings(query)
            
            if not query_embedding:
                return []
            
            # Tìm kiếm
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Parse kết quả
            documents = []
            if results and results['metadatas']:
                for metadata in results['metadatas'][0]:
                    documents.append({
                        "scholarship_name": metadata.get("scholarship_name", ""),
                        "url": metadata.get("url", ""),
                        "content": metadata.get("content", "")
                    })
            
            return documents
            
        except Exception as e:
            print(f"✗ Lỗi khi search RAG database: {e}")
            return []
