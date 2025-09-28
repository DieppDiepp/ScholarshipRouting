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
    collection: str = Query(..., description="Tên collection cần search"),
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
            index=collection, 
            size=size,
            offset=offset,
            collection=collection
        )
    finally:
        es.close()


@router.post("/sync")
def sync_firestore_to_es(
    collection: str = Query(..., description="Tên Firestore collection cần sync"),
):
    db = firestore.client()
    docs = db.collection(collection).stream()
    items = [{"id": doc.id, **doc.to_dict()} for doc in docs]

    if not items:
        return {"status": "ok", "message": f"No documents in collection '{collection}'"}

    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    try:
        count = index_many(es, items, index=collection, collection=collection)
        return {"status": "ok", "indexed": count, "collection": collection}
    finally:
        es.close()
