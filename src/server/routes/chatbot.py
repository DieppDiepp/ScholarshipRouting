from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from services.chatbot_thread2.main_app import ask_chatbot
from services.chatbot_thread1.main import ScholarshipChatbot

# Tạo router cho chatbot routes
router = APIRouter()

# Thiết lập logger
logger = logging.getLogger(__name__)

# Khởi tạo chatbot thread 1 (singleton)
chatbot_thread1 = None

def get_chatbot_thread1():
    """Lazy initialization của chatbot thread 1"""
    global chatbot_thread1
    if chatbot_thread1 is None:
        chatbot_thread1 = ScholarshipChatbot()
    return chatbot_thread1

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    message: str
    query: str
    answer: str
    scholarship_names: list[str]

class ErrorResponse(BaseModel):
    success: bool
    error: str

class ChatRequest(BaseModel):
    query: str
    profile_enabled: bool = False
    user_profile: Optional[Dict[str, Any]] = None
    timeout: int = 180

class ChatResponse(BaseModel):
    success: bool
    message: str
    query: str
    answer: str
    intent: str
    confidence: float
    tools_used: list[str]
    metadata: Dict[str, Any]

@router.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    """
    Route để xử lý câu hỏi từ người dùng thông qua RAG pipeline
    
    Expected JSON payload:
    {
        "query": "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu"
    }
    
    Returns:
    {
        "success": true,
        "message": "Query processed successfully",
        "query": "original query",
        "answer": "Câu trả lời từ chatbot",
        "scholarship_names": ["Danh sách tên học bổng"]
    }
    """
    try:
        query = request.query.strip()
        
        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        logger.info(f"Received query: {query}")
        
        # Gọi hàm ask_chatbot từ main_app.py và nhận kết quả
        result = ask_chatbot(query)
        
        # Trả về response với kết quả từ chatbot
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            query=query,
            answer=result.answer,
            scholarship_names=result.scholarship_names
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Route để xử lý câu hỏi từ người dùng thông qua chatbot thread 1
    với Intent Routing và Multi-Tool Retrieval
    
    Expected JSON payload:
    {
        "query": "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu",
        "profile_enabled": false,
        "user_profile": {
            "name": "Nguyen Van A",
            "gpa": 3.5,
            "field": "Computer Science"
        },
        "timeout": 180
    }
    
    Returns:
    {
        "success": true,
        "message": "Query processed successfully",
        "query": "original query",
        "answer": "Câu trả lời từ chatbot",
        "intent": "scholarship_search",
        "confidence": 0.95,
        "tools_used": ["semantic_search", "structured_query"],
        "metadata": {
            "semantic_results_count": 5,
            "structured_results_count": 3,
            "tavily_results_count": 0,
            "has_profile": false
        }
    }
    """
    try:
        query = request.query.strip()
        
        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        logger.info(f"Received chat query: {query}")
        
        # Lấy chatbot instance
        chatbot = get_chatbot_thread1()
        
        # Gọi hàm chat từ ScholarshipChatbot
        result = chatbot.chat(
            query=query,
            profile_enabled=request.profile_enabled,
            user_profile=request.user_profile,
            timeout=request.timeout
        )
        
        # Trả về response với kết quả từ chatbot
        return ChatResponse(
            success=True,
            message="Query processed successfully",
            query=result.get("query", query),
            answer=result.get("answer", ""),
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            tools_used=result.get("tools_used", []),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health():
    """
    Health check endpoint cho chatbot service
    """
    return {
        "success": True,
        "message": "Chatbot service is running",
        "service": "chatbot"
    }