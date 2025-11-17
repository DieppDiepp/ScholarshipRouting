from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from services.chatbot_thread2.main_app import ask_chatbot
from services.crm_svc import save_chat_to_user

# Tạo router cho chatbot routes
router = APIRouter()

# Thiết lập logger
logger = logging.getLogger(__name__)


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
    plan: str  # "basic" or "pro"
    user_id: Optional[str] = None  # Firebase UID or null

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
async def ask(request: ChatRequest):
    """
    Route để xử lý câu hỏi từ người dùng thông qua RAG pipeline
    
    Expected JSON payload:
    {
        "query": "Tôi muốn tìm học bổng toàn phần thạc sĩ ngành khoa học dữ liệu ở châu âu",
        "user_id": "user123" // Optional: if provided, chat will be saved to Firestore
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
        result = ask_chatbot(query, user_id=request.user_id)
        
        # Save chat to Firestore if user_id is provided
        if request.user_id:
            chat_data = {
                "id": f"chat_{int(datetime.utcnow().timestamp() * 1000)}",
                "query": query,
                "answer": result.answer,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "scholarship_names": result.scholarship_names,
                "plan": request.plan
            }
            save_chat_to_user(request.user_id, chat_data)
            logger.info(f"Chat saved for user: {request.user_id}")
        
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