import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from routes import health, firestore_routes, search , auth, user, chatbot, crm
import firebase_admin
from firebase_admin import credentials, firestore
from elasticsearch import Elasticsearch
from services.es_svc import index_many
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware

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
origins = [
    "http://localhost:3000",
    "https://scholarship-routing.vercel.app",
    "https://scholarshipsrouting.netlify.app"
]

def sync_firestore_to_es():
    """Sync Firestore collections to Elasticsearch (runs in background)"""
    import time
    
    es = Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        max_retries=5,
        retry_on_timeout=True,
        request_timeout=120,  # Increased to 120 seconds for bulk operations
    )

    try:
        print("🔄 Starting Firestore → Elasticsearch sync...")
        collections = db.collections()
        
        for coll_ref in collections:
            coll_name = coll_ref.id
            
            # Check if index exists and has data
            index_exists = es.indices.exists(index=coll_name)
            if index_exists:
                try:
                    # Check document count
                    doc_count = es.count(index=coll_name).get("count", 0)
                    if doc_count > 0:
                        print(f"⏭️  Skipping '{coll_name}' - already has {doc_count} documents")
                        continue
                    else:
                        print(f"📝 Index '{coll_name}' exists but empty, syncing...")
                except Exception as e:
                    print(f"⚠️  Could not check count for '{coll_name}': {e}. Skipping for now.")
                    continue
            else:
                print(f"📝 Creating new index '{coll_name}'...")
            
            # Stream documents from Firestore
            print(f"🔍 Fetching documents from Firestore collection '{coll_name}'...")
            docs = coll_ref.stream()
            records = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                records.append(data)

            if records:
                print(f"📦 Preparing to index {len(records)} documents...")
                
                # Wait for index to be ready (shards to activate)
                print(f"⏳ Waiting for index '{coll_name}' shards to become active...")
                max_wait = 30  # Wait up to 30 seconds
                for wait_attempt in range(max_wait):
                    try:
                        health = es.cluster.health(index=coll_name, timeout="5s")
                        if health.get("status") in ["yellow", "green"]:
                            print(f"✓ Index '{coll_name}' is ready ({health.get('status')})")
                            break
                    except Exception as e:
                        pass
                    
                    if wait_attempt < max_wait - 1:
                        time.sleep(1)
                else:
                    print(f"⚠️  Timeout waiting for '{coll_name}' to be ready, attempting anyway...")
                
                # Now try to index
                print(f"📦 Indexing documents in batches of 50...")
                result = index_many(
                    es,
                    records,
                    index=coll_name,
                    collection=coll_name,
                    batch_size=50  # Reduced from 100 to 50
                )
                
                if result.get("error"):
                    print(f"❌ Error syncing '{coll_name}': {result['error']}")
                else:
                    print(f"✅ Synced {result['success']}/{len(records)} docs from '{coll_name}'")
                    if result.get("failed", 0) > 0:
                        print(f"⚠️  {result['failed']} documents failed")
                
                # Add delay between collections
                print(f"💤 Waiting 5 seconds before next collection...")
                time.sleep(5)
            else:
                print(f"⚠️ No documents in collection '{coll_name}'")

        print("✅ Firestore → Elasticsearch sync completed successfully")

    except Exception as e:
        print(f"❌ Error syncing Firestore → ES: {e}")
        import traceback
        traceback.print_exc()
    finally:
        es.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup: Run sync in background thread to not block startup
    print("🚀 Application starting up...")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, sync_firestore_to_es)
    
    yield
    
    # Shutdown
    print("👋 Application shutting down...")

# --- FastAPI app ---
app = FastAPI(title="Scholarship Routing API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(firestore_routes.router, prefix="/api/v1/firestore", tags=["firestore"])
app.include_router(search.router, prefix="/api/v1/es", tags=["elasticsearch"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(crm.router, prefix="/api/v1/crm", tags=["crm"])
Instrumentator().instrument(app).expose(app)
