import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import health, firestore_routes, search
import firebase_admin
from firebase_admin import credentials, firestore
from elasticsearch import Elasticsearch
from services.es_svc import index_many

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

@app.on_event("startup")
def sync_firestore_to_es():
    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    try:
        docs = db.collection("scholarships").stream()
        records = [doc.to_dict() for doc in docs]
        if records:
            count = index_many(es, records, index=os.getenv("ELASTICSEARCH_INDEX", "scholarships"), collection="scholarship")
            print(f"✅ Synced {count} docs from Firestore → ES")
        else:
            print("⚠️ No documents found in Firestore")
    except Exception as e:
        print(f"❌ Error syncing Firestore → ES: {e}")
    finally:
        es.close()