# routes/search.py
import os
from typing import Any, Dict, List, Union, Optional, Literal
from fastapi import APIRouter, Body, Query
from elasticsearch import Elasticsearch
from services.es_svc import search_keyword, index_many, filter_advanced
from firebase_admin import firestore
from dtos.search_dtos import FilterItem

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
        max_retries=3,
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
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Search failed. Elasticsearch may be overloaded. Please try again.",
            "total": 0,
            "items": []
        }
    finally:
        es.close()


@router.post("/sync")
def sync_firestore_to_es(
    collection: str = Query(..., description="Tên Firestore collection cần sync"),
    force: bool = Query(False, description="Force resync even if data exists"),
):
    """Manual sync endpoint - use cautiously as ES may be under load from background sync"""
    try:
        # Check ES health first
        es = Elasticsearch(
            hosts=[ES_HOST],
            basic_auth=(ES_USER, ES_PASS),
            verify_certs=False,
            max_retries=3,
            retry_on_timeout=True,
            request_timeout=30,
        )
        
        try:
            # Quick health check
            health = es.cluster.health(timeout="5s")
            cluster_status = health.get("status", "unknown")
            
            if cluster_status == "red":
                return {
                    "status": "error",
                    "message": f"Elasticsearch cluster is unhealthy (status: {cluster_status}). Cannot sync now.",
                    "collection": collection,
                    "suggestion": "Wait for background sync to complete or check ES resources"
                }
            
            if cluster_status == "yellow":
                print(f"⚠️  ES cluster status is YELLOW, syncing may be slow...")
                
        except Exception as health_error:
            return {
                "status": "error", 
                "message": f"Cannot connect to Elasticsearch: {str(health_error)}",
                "collection": collection
            }
        
        db = firestore.client()
        
        try:
            # Check if index already has data
            if not force and es.indices.exists(index=collection):
                try:
                    doc_count = es.count(index=collection).get("count", 0)
                    if doc_count > 0:
                        return {
                            "status": "skipped",
                            "message": f"Index '{collection}' already has {doc_count} documents. Use force=true to resync.",
                            "existing_documents": doc_count,
                            "collection": collection
                        }
                except Exception as count_error:
                    # If count fails (e.g., ES overloaded), log and continue with sync
                    print(f"⚠️  Could not check document count for '{collection}': {count_error}")
                    print(f"   Proceeding with sync attempt anyway...")
            
            docs = db.collection(collection).stream()
            items = [{"id": doc.id, **doc.to_dict()} for doc in docs]

            if not items:
                return {"status": "ok", "message": f"No documents in collection '{collection}'"}

            result = index_many(
                es, 
                items, 
                index=collection, 
                collection=collection,
                batch_size=50  # Process in smaller batches
            )
            
            return {
                "status": "ok",
                "total_documents": len(items),
                "indexed": result["success"],
                "failed": result["failed"],
                "duplicates": result.get("duplicates", 0),
                "failed_records": result["failed_ids"][:10],  # Limit to first 10
                "collection": collection
            }
        finally:
            es.close()
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "collection": collection,
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

filter_example = [
    {
      "field": "Country",
      "values": ["Hà Lan", "Đức"],
      "operator": "OR"
    },
    {
      "field": "Funding_Level",
      "values": ["Toàn phần"],
      "operator": "OR"
    }
]

@router.post("/filter")
def filter_documents(
    # --- Các tham số Query Parameter ---
    collection: str = Query(..., description="Tên collection cần filter"),
    size: int = Query(10, ge=1, le=100, description="Số lượng kết quả trả về"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu lấy kết quả"),
    inter_field_operator: Literal["AND", "OR"] = Query("AND", description="Toán tử kết hợp các bộ lọc với nhau"),
    
    # --- Request body giờ là một danh sách FilterItem ---
    filters: List[FilterItem] = Body(..., examples=[filter_example])
):
    """
    API để lọc document với các điều kiện phức tạp.
    """
    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        max_retries=3,
        retry_on_timeout=True,
        request_timeout=30,
    )
    try:
        # Chuyển đổi list các Pydantic model thành list các dict
        filters_dict = [item.model_dump() for item in filters]

        return filter_advanced(
            client=es,
            index=collection,
            collection=collection,
            filters=filters_dict,
            inter_field_operator=inter_field_operator,
            size=size,
            offset=offset
        )
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Filter operation failed. Elasticsearch may be overloaded. Please try again.",
            "total": 0,
            "items": []
        }
    finally:
        es.close()