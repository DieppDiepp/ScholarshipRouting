# routes/search.py
import os
from typing import Any, Dict, List, Union, Optional
from fastapi import APIRouter, Query
from elasticsearch import Elasticsearch
from services.es_svc import search_keyword, index_many
from firebase_admin import firestore

router = APIRouter()
ES_HOST = os.getenv("ELASTICSEARCH_HOST")
ES_USER = os.getenv("ELASTIC_USER")
ES_PASS = os.getenv("ELASTIC_PASSWORD")
@router.get("/search")
def search(
    q: str = Query(..., description="Từ khóa full-text"),
    size: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    collection: Optional[str] = Query(None, description="Lọc theo collection nếu cần"),
):
    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),  
        verify_certs=False,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    try:
        return search_keyword(
            es, q,
            index="scholarships",
            size=size,
            offset=offset,
            collection=collection
        )
    finally:
        es.close() 

@router.post("/sync")
def sync_firestore_to_es():
    """Đồng bộ dữ liệu từ Firestore collection -> Elasticsearch index"""
    db = firestore.client()
    docs = db.collection("scholarships").stream()

    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  
        items.append(data)

    if not items:
        return {"status": "ok", "message": "No documents found in Firestore"}

    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    try:
        count = index_many(es, items, index="scholarships", collection="scholarship")
        return {"status": "ok", "indexed": count}
    finally:
        es.close()