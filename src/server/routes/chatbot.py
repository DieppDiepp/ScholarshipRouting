from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from services.chatbot_thread2.main_app import ask_chatbot

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

class ErrorResponse(BaseModel):
    success: bool
    error: str

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
        "query": "original query"
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
        
        # Gọi hàm ask_chatbot từ main_app.py
        ask_chatbot(query)
        
        # Trả về response thành công
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            query=query
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