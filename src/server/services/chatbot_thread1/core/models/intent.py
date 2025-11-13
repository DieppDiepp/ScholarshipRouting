"""
Module định nghĩa các loại Intent (Ý định) của người dùng
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any

class IntentType(Enum):
    """Enum định nghĩa các loại intent theo sơ đồ"""
    FACT_RETRIEVAL = "fact_retrieval"  # Case 1.1: Tìm chi tiết
    FILTERING = "filtering"  # Case 1.2/1.4: Lọc/Liệt kê
    STATIC_COMPARISON = "static_comparison"  # Case 1.3: So sánh tĩnh
    GENERAL_ADVICE = "general_advice"  # Case 2.1: Tư vấn chung
    EXTERNAL_QA = "external_qa"  # Case 2.2: Hỏi đáp ngoài luồng
    PERSONALIZED_ADVICE = "personalized_advice"  # Case 2.3: Tư vấn cá nhân hóa
    PERSONALIZED_RECOMMENDATION = "personalized_recommendation"  # Case 2.4: Đề xuất cá nhân hóa

class Intent(BaseModel):
    """Model đại diện cho Intent được phát hiện"""
    intent_type: IntentType
    confidence: float  # Độ tin cậy (0-1)
    extracted_params: Optional[Dict[str, Any]] = None  # Các tham số trích xuất từ query
    
    def __str__(self):
        return f"Intent: {self.intent_type.value} (confidence: {self.confidence:.2f})"
