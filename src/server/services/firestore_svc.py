import re
from typing import Optional, Dict, Any
from firebase_admin import firestore

# regex chặn tên collection nguy hiểm
_COLLECTION_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")

def _ensure_valid_collection(collection: str) -> str:
    if not _COLLECTION_RE.match(collection):
        raise ValueError("Invalid collection name")
    return collection

def get_db():
    """Đảm bảo client chỉ lấy khi app đã initialize"""
    return firestore.client()

def save_doc(collection: str, doc_id: Optional[str], data: Dict[str, Any]) -> str:
    col = _ensure_valid_collection(collection)
    db = get_db()
    if doc_id:
        ref = db.collection(col).document(doc_id)
        ref.set(data, merge=True)
        return doc_id
    ref = db.collection(col).document()  # auto id
    ref.set(data, merge=True)
    return ref.id

def get_doc(collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    col = _ensure_valid_collection(collection)
    db = get_db()
    snap = db.collection(col).document(doc_id).get()
    return snap.to_dict() if snap.exists else None
