"""
Tool 1: Semantic Search - Tìm kiếm ngữ nghĩa trên Vector Database
Kết hợp Structured JSON + RAG Database
Refactored to use Langchain BaseTool
"""
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import Field
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.utils.api_key_manager import get_next_gemini_key

class SemanticSearchTool(BaseTool):
    """Tool tìm kiếm ngữ nghĩa sử dụng ChromaDB và Gemini Embeddings"""
    
    name: str = "semantic_search"
    description: str = """Search for scholarships based on semantics (semantic search).
    Use when detailed information about specific scholarships is needed.
    Input: question or scholarship name.
    Output: list of matching scholarships with detailed information."""
    
    # Custom fields
    client: Any = Field(default=None, exclude=True)
    collection: Any = Field(default=None, exclude=True)
    collection_name: str = Field(default="scholarships", exclude=True)
    use_rag: bool = Field(default=True, exclude=True)
    rag_tool: Any = Field(default=None, exclude=True)
    
    def __init__(self, use_rag: bool = True, **kwargs):
        """Khởi tạo Semantic Search Tool"""
        super().__init__(**kwargs)
        
        # Cấu hình Gemini API với key rotation
        genai.configure(api_key=get_next_gemini_key())
        
        # Khởi tạo ChromaDB client
        self.client = chromadb.PersistentClient(
            path=Config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Tên collection cho structured data
        self.collection_name = "scholarships"
        self.collection = None
        
        # RAG Search Tool
        self.use_rag = use_rag
        self.rag_tool = None
        if use_rag:
            try:
                from services.chatbot_thread1.core.tools.rag_search import RAGSearchTool
                self.rag_tool = RAGSearchTool()
            except Exception as e:
                print(f"⚠ Không thể load RAG tool: {e}")
                self.use_rag = False

    
    def create_embeddings(self, text: str) -> List[float]:
        """
        Tạo embedding vector từ text sử dụng Gemini
        
        Args:
            text: Văn bản cần tạo embedding
            
        Returns:
            List các số thực đại diện cho embedding vector
        """
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
    
    def index_scholarships(self, scholarships: List[Dict[str, Any]]):
        """
        Đánh chỉ mục (index) các học bổng vào vector database
        
        Args:
            scholarships: Danh sách các học bổng cần index
        """
        try:
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
            
            # Chuẩn bị dữ liệu để index
            documents = []
            metadatas = []
            ids = []
            
            for idx, scholarship in enumerate(scholarships):
                # Tạo document text từ các trường quan trọng
                doc_parts = []
                
                name = scholarship.get("Scholarship_Name", "")
                doc_parts.append(f"Tên học bổng: {name}")
                
                country = scholarship.get("Country", "")
                if country:
                    doc_parts.append(f"Quốc gia: {country}")
                
                info = scholarship.get("Scholarship_Info", "")
                if info:
                    doc_parts.append(f"Thông tin: {info}")
                
                eligibility = scholarship.get("Eligibility_Criteria", "")
                if eligibility:
                    doc_parts.append(f"Điều kiện: {eligibility}")
                
                fields = scholarship.get("Eligible_Fields", "")
                if fields:
                    doc_parts.append(f"Ngành học: {fields}")
                
                document = "\n".join(doc_parts)
                documents.append(document)
                
                # Metadata (lưu toàn bộ scholarship data dưới dạng JSON string)
                import json
                metadatas.append({"data": json.dumps(scholarship, ensure_ascii=False)})
                
                # ID duy nhất
                ids.append(f"scholarship_{idx}")
            
            # Tạo embeddings cho tất cả documents
            print(f"Đang tạo embeddings cho {len(documents)} học bổng...")
            embeddings = []
            for doc in documents:
                emb = self.create_embeddings(doc)
                embeddings.append(emb)
            
            # Thêm vào collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✓ Đã index {len(scholarships)} học bổng vào vector database")
            
        except Exception as e:
            print(f"✗ Lỗi khi index scholarships: {e}")
    
    def _run(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Langchain BaseTool _run method
        
        Args:
            query: Câu hỏi/truy vấn của người dùng
            top_k: Số lượng kết quả trả về
            
        Returns:
            String representation của kết quả
        """
        results = self.search(query, top_k)
        
        # Format results as string
        if not results:
            return "Không tìm thấy học bổng phù hợp."
        
        output = []
        for idx, scholarship in enumerate(results, 1):
            name = scholarship.get("Scholarship_Name", "Unknown")
            country = scholarship.get("Country", "N/A")
            funding = scholarship.get("Funding_Level", "N/A")
            output.append(f"{idx}. {name} ({country}) - {funding}")
        
        return "\n".join(output)
    
    def search(self, query: str, top_k: int = None, use_rag: bool = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm học bổng dựa trên query
        Kết hợp Structured JSON + RAG Database
        
        Args:
            query: Câu hỏi/truy vấn của người dùng
            top_k: Số lượng kết quả trả về (mặc định lấy từ Config)
            use_rag: Có sử dụng RAG database không (mặc định True)
            
        Returns:
            List các học bổng phù hợp nhất (kết hợp structured + RAG)
        """
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        if use_rag is None:
            use_rag = self.use_rag
        
        # Kết quả từ structured search
        structured_results = self._search_structured(query, top_k)
        
        # Kết quả từ RAG search (nếu enabled)
        rag_results = []
        if use_rag and self.rag_tool:
            try:
                rag_results = self.rag_tool.search(query, top_k=3)
            except Exception as e:
                print(f"⚠ Lỗi RAG search: {e}")
        
        # Merge results
        return self._merge_results(structured_results, rag_results)
    
    def _search_structured(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Tìm kiếm trên structured JSON"""
        try:
            # Load collection nếu chưa load
            if self.collection is None:
                self.collection = self.client.get_collection(name=self.collection_name)
            
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
            scholarships = []
            if results and results['metadatas']:
                import json
                for metadata in results['metadatas'][0]:
                    scholarship_data = json.loads(metadata['data'])
                    scholarships.append(scholarship_data)
            
            return scholarships
            
        except Exception as e:
            print(f"✗ Lỗi khi search structured: {e}")
            return []
    
    def _merge_results(self, structured: List[Dict], rag: List[Dict]) -> List[Dict]:
        """
        Merge kết quả từ structured JSON và RAG database
        
        Args:
            structured: Kết quả từ structured JSON
            rag: Kết quả từ RAG database
            
        Returns:
            List kết quả đã merge (structured + RAG info)
        """
        # Nếu không có RAG results, trả về structured
        if not rag:
            return structured
        
        # Tạo map từ scholarship name -> RAG info
        rag_map = {}
        for rag_doc in rag:
            name = rag_doc.get("scholarship_name", "")
            if name:
                rag_map[name] = {
                    "url": rag_doc.get("url", ""),
                    "web_content": rag_doc.get("content", "")
                }
        
        # Thêm RAG info vào structured results
        merged = []
        for scholarship in structured:
            name = scholarship.get("Scholarship_Name", "")
            
            # Thêm RAG info nếu có
            if name in rag_map:
                scholarship["RAG_URL"] = rag_map[name]["url"]
                scholarship["RAG_Content"] = rag_map[name]["web_content"]
            
            merged.append(scholarship)
        
        return merged
