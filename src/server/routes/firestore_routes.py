from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from services.firestore_svc import save_doc, get_doc

router = APIRouter()

class DocIn(BaseModel):
    id: Optional[str] = Field(default=None, description="Document id (optional).")
    data: Dict[str, Any]

class DocOut(BaseModel):
    id: str
    data: Dict[str, Any]

@router.post("/{collection}", response_model=DocOut)
def upsert_document(collection: str, payload: DocIn):
    try:
        doc_id = save_doc(collection, payload.id, payload.data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid collection name")
    return DocOut(id=doc_id, data=payload.data)

@router.get("/{collection}/{doc_id}", response_model=DocOut)
def read_document(collection: str, doc_id: str):
    try:
        doc = get_doc(collection, doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid collection name")
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return DocOut(id=doc_id, data=doc)
