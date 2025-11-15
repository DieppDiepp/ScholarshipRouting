"""
CRM Service - Business logic for admin dashboard and user management
"""
import os
from typing import List, Dict, Any, Optional
from firebase_admin import firestore
from datetime import datetime


def get_firestore_client():
    """Get Firestore client instance"""
    return firestore.client()


def verify_admin_token(token: str) -> bool:
    """
    Verify if the provided token belongs to an admin user
    
    Args:
        token: Firebase ID token
        
    Returns:
        True if user is admin, False otherwise
    """
    # TODO: Implement proper admin verification
    # For now, check against env variable or Firestore admin collection
    admin_token = os.getenv("ADMIN_TOKEN")
    if admin_token and token == admin_token:
        return True
    
    # Alternative: Check Firestore for admin role
    try:
        from firebase_admin import auth
        decoded = auth.verify_id_token(token)
        uid = decoded.get("uid")
        
        db = get_firestore_client()
        user_doc = db.collection("users").document(uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get("role") == "admin"
    except Exception:
        pass
    
    return False


def get_dashboard_stats() -> Dict[str, Any]:
    """
    Get overall dashboard statistics
    
    Returns:
        Dictionary containing:
        - total_users: Total number of users with chat history
        - total_chats: Total number of chat interactions
        - chats_today: Number of chats today
        - active_users: Users who chatted in last 7 days
    """
    db = get_firestore_client()
    
    # Get all users with chatHistory field
    users_ref = db.collection("users")
    users = users_ref.stream()
    
    total_users = 0
    total_chats = 0
    chats_today = 0
    active_users_set = set()
    
    today = datetime.utcnow().date()
    seven_days_ago = datetime.utcnow().timestamp() - (7 * 24 * 60 * 60)
    
    for user_doc in users:
        user_data = user_doc.to_dict()
        chat_history = user_data.get("chatHistory", [])
        
        if not chat_history:
            continue
        
        total_users += 1
        total_chats += len(chat_history)
        
        for chat in chat_history:
            timestamp_str = chat.get("timestamp", "")
            try:
                # Parse ISO timestamp
                chat_date = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                
                if chat_date.date() == today:
                    chats_today += 1
                
                if chat_date.timestamp() >= seven_days_ago:
                    active_users_set.add(user_doc.id)
            except (ValueError, AttributeError):
                continue
    
    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "chats_today": chats_today,
        "active_users": len(active_users_set),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def get_users_with_chats(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get list of users who have chat history
    
    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip
        
    Returns:
        List of user objects with basic info and chat count
    """
    db = get_firestore_client()
    
    users_ref = db.collection("users")
    users = users_ref.stream()
    
    result = []
    current_index = 0
    
    for user_doc in users:
        user_data = user_doc.to_dict()
        chat_history = user_data.get("chatHistory", [])
        
        if not chat_history:
            continue
        
        if current_index < offset:
            current_index += 1
            continue
        
        if len(result) >= limit:
            break
        
        # Get last chat timestamp
        last_chat = None
        if chat_history:
            last_chat = chat_history[-1].get("timestamp")
        
        result.append({
            "user_id": user_doc.id,
            "email": user_data.get("email"),
            "display_name": user_data.get("display_name"),
            "chat_count": len(chat_history),
            "last_chat_at": last_chat,
            "created_at": user_data.get("created_at")
        })
        
        current_index += 1
    
    return result


def get_user_chat_history(user_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get chat history for a specific user
    
    Args:
        user_id: User ID to fetch chats for
        limit: Maximum number of chats to return
        offset: Number of chats to skip
        
    Returns:
        List of chat objects
        
    Raises:
        ValueError: If user not found
    """
    db = get_firestore_client()
    
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise ValueError(f"User with ID '{user_id}' not found")
    
    user_data = user_doc.to_dict()
    chat_history = user_data.get("chatHistory", [])
    
    # Apply pagination
    paginated_chats = chat_history[offset:offset + limit]
    
    return paginated_chats


def save_chat_to_user(user_id: str, chat_data: Dict[str, Any]) -> bool:
    """
    Save a chat interaction to user's chat history
    
    Args:
        user_id: User ID to save chat for
        chat_data: Chat data containing query, answer, timestamp, etc.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        user_ref = db.collection("users").document(user_id)
        
        # Check if user exists, if not create with basic structure
        user_doc = user_ref.get()
        if not user_doc.exists:
            # Create new user document with empty chatHistory
            user_ref.set({
                "email": "",
                "firstName": "",
                "lastName": "",
                "chatHistory": []
            })
        
        # Add timestamp if not provided
        if "timestamp" not in chat_data:
            chat_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Add unique chat ID if not provided
        if "id" not in chat_data:
            chat_data["id"] = f"chat_{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Add plan if not provided
        if "plan" not in chat_data:
            chat_data["plan"] = "basic"
        
        # Append to chatHistory array
        user_ref.update({
            "chatHistory": firestore.ArrayUnion([chat_data])
        })
        
        return True
    except Exception:
        return False
