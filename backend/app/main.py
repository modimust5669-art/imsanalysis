import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.seed_data import seed_database
from app.routes.public_routes import router as public_router
from app.routes.admin_routes import router as admin_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = os.path.join(BASE_DIR, "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed PDF data on start
    init_db()
    seed_database()
    yield

app = FastAPI(
    title="LIPTIS USA SALs App API",
    description="Corporate Event and Itinerary Management System for LIPTIS USA",
    version="1.0.0",
    lifespan=lifespan
)

# Ensure database is initialized for serverless runtimes
try:
    init_db()
    seed_database()
except Exception as e:
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(public_router)
app.include_router(admin_router)

# Mount Static Files
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "LIPTIS USA SALs App Backend running. Frontend index.html loading."}

@app.get("/manifest.json")
def get_manifest():
    manifest_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json")
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

@app.get("/sw.js")
def get_service_worker():
    sw_path = os.path.join(STATIC_DIR, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    return JSONResponse(status_code=404, content={"detail": "Service worker not found"})

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "LIPTIS USA SALs App",
        "organization": "LIPTIS USA",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
