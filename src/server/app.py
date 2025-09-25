from fastapi import FastAPI
from routes import health

app = FastAPI(title="Scholarship Routing API")
app.include_router(health.router, prefix="/health", tags=["health"])
