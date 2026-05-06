from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import Base, engine
import json

app = FastAPI(title="Metro Safety Dashboard API")

# Setup CORS
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    try:
        origins = json.loads(origins)
    except:
        origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.auth.routes import router as auth_router
from app.api.epp_routes import router as epp_router
from app.api.excavation_routes import router as excavation_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.events_routes import router as events_router
from app.api.export_routes import router as export_router

app.include_router(auth_router)
app.include_router(epp_router)
app.include_router(excavation_router)
app.include_router(dashboard_router)
app.include_router(events_router)
app.include_router(export_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
