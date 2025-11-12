"""
FastAPI Server cho Scholarship Chatbot
Cung cấp REST API endpoints để tương tác với chatbot
"""
import sys
from pathlib import Path

# Thêm thư mục cha vào Python path để import được các module
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from main import ScholarshipChatbot
from core.utils.data_loader import DataLoader

# Khởi tạo FastAPI app
app = FastAPI(
    title="Scholarship Chatbot API",
    description="API for scholarship recommendation chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo chatbot và data loader
chatbot = ScholarshipChatbot()
data_loader = DataLoader()

# Pydantic models
class ChatRequest(BaseModel):
    query: str
    profile_enabled: bool = False
    user_profile: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    query: str
    answer: str
    intent: str
    confidence: float
    tools_used: List[str]
    metadata: Dict[str, Any]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Scholarship Chatbot API is running",
        "version": "1.0.0"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Gửi câu hỏi và nhận câu trả lời
    
    Args:
        request: ChatRequest chứa query và profile (optional)
        
    Returns:
        ChatResponse chứa câu trả lời và metadata
    """
    try:
        result = chatbot.chat(
            query=request.query,
            profile_enabled=request.profile_enabled,
            user_profile=request.user_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholarships/countries")
async def get_countries():
    """Lấy danh sách tất cả các quốc gia có học bổng"""
    try:
        countries = data_loader.get_countries()
        return {
            "countries": countries,
            "count": len(countries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholarships/fields")
async def get_fields():
    """Lấy danh sách tất cả các ngành học"""
    try:
        fields = data_loader.get_fields()
        return {
            "fields": fields,
            "count": len(fields)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholarships/search")
async def search_scholarships(
    country: Optional[str] = None,
    field: Optional[str] = None,
    degree: Optional[str] = None,
    funding: Optional[str] = None
):
    """
    Tìm kiếm học bổng theo các tiêu chí
    
    Query params:
        - country: Quốc gia
        - field: Ngành học
        - degree: Bậc học (Bachelor, Master, PhD)
        - funding: Mức tài trợ (Full, Partial)
    """
    try:
        filters = {}
        if country:
            filters["Country"] = country
        if field:
            filters["Eligible_Fields"] = field
        if degree:
            filters["Required_Degree"] = degree
        if funding:
            filters["Funding_Level"] = funding
        
        results = data_loader.filter_scholarships(filters)
        
        return {
            "scholarships": results,
            "count": len(results),
            "filters": filters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholarships/{scholarship_name}")
async def get_scholarship_details(scholarship_name: str):
    """Lấy thông tin chi tiết của một học bổng"""
    try:
        scholarship = data_loader.get_scholarship_by_name(scholarship_name)
        
        if not scholarship:
            raise HTTPException(
                status_code=404,
                detail=f"Scholarship '{scholarship_name}' not found"
            )
        
        return scholarship
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting FastAPI Server")
    print("="*60)
    print("📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
