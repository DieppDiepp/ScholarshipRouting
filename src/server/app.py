import os
from fastapi import FastAPI
from routes import health, firestore_routes
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not firebase_admin._apps:
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS env")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

app = FastAPI(title="Scholarship Routing API")
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(firestore_routes.router, prefix="/api/v1/firestore", tags=["firestore"])
