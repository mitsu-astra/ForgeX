import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.config import settings
from backend.app.services.model_service import get_model_service
from backend.app.routers import quality, process, correlation, simulator, upload, copilot, analytics, auth, system, control, reports

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifespan event handler.
    Preloads all AI & Deep Learning models into memory.
    """
    logger.info("=" * 70)
    logger.info(" STARTING FORGEX • INDUSTRIAL DECISION INTELLIGENCE API")
    logger.info("=" * 70)

    # Initialize models
    model_service = get_model_service()
    model_service.initialize(
        vision_weights=settings.VISION_MODEL_WEIGHTS,
        correlation_weights=settings.CORRELATION_MODEL_WEIGHTS,
    )
    logger.info("[✓] All ForgeX core engines initialized.")

    # Initialize PostgreSQL Database and seed materials
    from backend.app.db.db_service import init_database
    init_database()

    yield

    logger.info("Shutting down ForgeX Decision Intelligence API...")


# Create FastAPI application
app = FastAPI(
    title="ForgeX • Industrial Decision Intelligence API",
    description="ForgeX • Industrial Decision Intelligence — Multi-Modal Visual Inspection, Discrete-Event Process Surrogates, Root-Cause Explainability, and What-If Simulation API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads directory for static asset viewing
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount Dataset Train directory for real specimen image serving
train_dir = os.path.join(root_dir, "train")
if os.path.exists(train_dir):
    app.mount("/static/train", StaticFiles(directory=train_dir), name="train")

# Include Routers
app.include_router(auth.router)
app.include_router(system.router)
app.include_router(upload.router)
app.include_router(quality.router)
app.include_router(process.router)
app.include_router(correlation.router)
app.include_router(simulator.router)
app.include_router(copilot.router)
app.include_router(analytics.router)
app.include_router(control.router)
app.include_router(reports.router)


@app.get("/health", tags=["Health"])
async def health_check():
    model_service = get_model_service()
    return {
        "status": "healthy",
        "service": "ForgeX • Industrial Decision Intelligence API",
        "vision_engine_loaded": model_service.vision_engine is not None,
        "bottleneck_detector_loaded": model_service.bottleneck_detector is not None,
        "root_cause_classifier_loaded": model_service.root_cause_classifier is not None,
        "what_if_simulator_loaded": model_service.what_if_simulator is not None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
