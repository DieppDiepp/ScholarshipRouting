from typing import Optional, Dict, Any, List, Union
from fastapi import APIRouter, HTTPException,Query,Body
from pydantic import BaseModel, Field
from services.firestore_svc import save_one_raw, save_many_raw, get_one_raw
router = APIRouter()

class DocOut(BaseModel):
    id: str
    data: Dict[str, Any]

@router.post("/{collection}")
def upsert_documents(
    collection: str,
    payload: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(
        ..., 
        example={"Scholarship_Name": "Chevening", "Country": "UK"}
    ),
):
    """
    Upsert document(s) vào Firestore.
    - Nếu body là 1 object → lưu 1 record.
    - Nếu body là 1 array object → lưu nhiều record.
    - Doc_id sẽ được auto-generate.
    """
    try:
        if isinstance(payload, list):
            ids = save_many_raw(collection, rows=payload)
            return {"inserted_ids": ids}
        else:
            saved_id = save_one_raw(collection, data=payload)
            return {"id": saved_id, "data": payload}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid collection name")

@router.get("/{collection}/{doc_id}", response_model=DocOut)
def read_document(collection: str, doc_id: str):
    try:
        doc = get_one_raw(collection, doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid collection name")
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return DocOut(id=doc_id, data=doc)
