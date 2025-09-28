import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import health, firestore_routes, search , auth, user
import firebase_admin
from firebase_admin import credentials, firestore
from elasticsearch import Elasticsearch
from services.es_svc import index_many
from prometheus_fastapi_instrumentator import Instrumentator

ES_HOST = os.getenv("ELASTICSEARCH_HOST")
ES_USER = os.getenv("ELASTIC_USER")
ES_PASS = os.getenv("ELASTIC_PASSWORD")
# --- Firebase init ---
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not firebase_admin._apps:
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS env")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- FastAPI app ---
app = FastAPI(title="Scholarship Routing API")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(firestore_routes.router, prefix="/api/v1/firestore", tags=["firestore"])
app.include_router(search.router, prefix="/api/v1/es", tags=["elasticsearch"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
Instrumentator().instrument(app).expose(app)
@app.on_event("startup")
def sync_all_firestore_collections_to_es():
    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )

    try:
        collections = db.collections()  # Lấy tất cả Firestore collections
        for coll_ref in collections:
            coll_name = coll_ref.id
            docs = coll_ref.stream()
            records = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id  # gắn id để tránh trùng
                records.append(data)

            if records:
                count = index_many(
                    es,
                    records,
                    index=coll_name,        # mỗi collection map sang 1 index cùng tên
                    collection=coll_name    # gắn tên collection để filter khi search
                )
                print(f"✅ Synced {count} docs from Firestore collection '{coll_name}' → ES index '{coll_name}'")
            else:
                print(f"⚠️ No documents found in collection '{coll_name}'")

    except Exception as e:
        print(f"❌ Error syncing Firestore → ES: {e}")
    finally:
        es.close()
