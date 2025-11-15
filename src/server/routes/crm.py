"""
CRM Routes - Admin endpoints for user chat management
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime
from services.crm_svc import (
    get_dashboard_stats,
    get_users_with_chats,
    get_user_chat_history
)

router = APIRouter()


@router.get("/stats")
async def get_stats():
    """
    Get dashboard statistics
    
    Returns: Overall chat statistics
    """
    
    try:
        stats = get_dashboard_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def list_users(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    List all users with chat activity
    
    Query params:
        - limit: Number of users to return (default: 50, max: 500)
        - offset: Pagination offset (default: 0)
    """
    
    try:
        users = get_users_with_chats(limit=limit, offset=offset)
        return {
            "success": True,
            "data": users,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(users)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/chats")
async def get_user_chats(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get chat history for a specific user
    
    Path params:
        - user_id: User ID to fetch chats for
    Query params:
        - limit: Number of chats to return (default: 100, max: 1000)
        - offset: Pagination offset (default: 0)
    """
    
    try:
        chats = get_user_chat_history(user_id, limit=limit, offset=offset)
        return {
            "success": True,
            "user_id": user_id,
            "data": chats,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(chats)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
