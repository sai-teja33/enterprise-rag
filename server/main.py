from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.mongo import ping_mongodb

from api.routes.documents import router as documents_router
from api.routes.query import router as query_router
from api.routes.health import router as health_router


app = FastAPI(title="Enterprise RAG API")


@app.get("/")
def root():
    return {"message": "Enterprise RAG API is running"}


@app.get("/health")
def health_check():
    mongo_ok = ping_mongodb()
    return {
        "api": "ok",
        "mongodb": "connected" if mongo_ok else "failed"
    }

# CORS for Angular / frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(documents_router)
app.include_router(query_router)
app.include_router(health_router)
