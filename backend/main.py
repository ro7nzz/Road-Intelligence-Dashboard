from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine, Base
from backend.routers.detect import router as detect_router
from backend.routers.analyze import router as analyze_router

# Create SQLite database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RoadAI API",
    description="AI-Powered Road Damage Intelligence & Repair Prioritization System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "https://road-intelligence-dashboard.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect_router)
app.include_router(analyze_router)


@app.get("/")
def root():
    return {
        "message": "RoadAI API is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RoadAI Backend",
    }
