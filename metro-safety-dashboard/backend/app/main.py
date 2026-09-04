from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database.connection import Base, engine
import app.models  # Registra todos los modelos antes de crear las tablas
import json
import os

app = FastAPI(title="Metro Safety Dashboard API")
Base.metadata.create_all(bind=engine)

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

# Setup Static Files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(os.path.join(STATIC_DIR, "images"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount Frontend UI files over HTTP
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

from app.auth.routes import router as auth_router
from app.api.epp_routes import router as epp_router
from app.api.excavation_routes import router as excavation_router
from app.api.milesight_routes import router as milesight_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.events_routes import router as events_router
from app.api.export_routes import router as export_router
from app.api.cycle_routes import router as cycle_router
from app.api.cycle_lora_routes import router as cycle_lora_router

app.include_router(auth_router)
app.include_router(epp_router)
app.include_router(excavation_router)
app.include_router(milesight_router)
app.include_router(dashboard_router)
app.include_router(events_router)
app.include_router(export_router)
app.include_router(cycle_router)
app.include_router(cycle_lora_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
from pathlib import Path

import sqlite3 as _sqlite3



@app.get("/api/dashboard/epp-metrics")
@app.get("/dashboard/epp-metrics")

def dashboard_epp_metrics(minutes: int = 15):

    if minutes < 1:

        minutes = 15



    if minutes > 1440:

        minutes = 1440



    db_path = Path(__file__).resolve().parents[1] / "sql_app.db"

    conn = _sqlite3.connect(str(db_path))

    conn.row_factory = _sqlite3.Row

    cur = conn.cursor()



    latest_row = cur.execute(

        "SELECT MAX(timestamp) AS max_ts FROM epp_events"

    ).fetchone()



    latest = latest_row["max_ts"] if latest_row else None



    if not latest:

        conn.close()

        return {

            "window_minutes": minutes,

            "latest_timestamp": None,

            "events_epp_evaluated": 0,

            "events_compliant": 0,

            "events_non_compliant": 0,

            "compliance_observed_pct": 0,

            "most_missing_epp": "-",

            "most_missing_epp_count": 0,

            "dominant_alert_level": "-",

            "dominant_alert_count": 0,

            "epp_breakdown": [

                {"name": "Casco", "detected_pct": 0},

                {"name": "Guantes", "detected_pct": 0},

                {"name": "Antiparras", "detected_pct": 0},

                {"name": "Chaleco reflectante", "detected_pct": 0},

                {"name": "Mascarilla", "detected_pct": 0},

            ],

        }



    modifier = f"-{minutes} minutes"



    summary = cur.execute(

        """

        SELECT

            COUNT(*) AS total,

            COALESCE(SUM(CASE WHEN non_compliance_detected = 0 THEN 1 ELSE 0 END), 0) AS compliant,

            COALESCE(SUM(CASE WHEN non_compliance_detected = 1 THEN 1 ELSE 0 END), 0) AS non_compliant

        FROM epp_events

        WHERE timestamp >= datetime(?, ?)

        """,

        (latest, modifier),

    ).fetchone()



    total = int(summary["total"] or 0)

    compliant = int(summary["compliant"] or 0)

    non_compliant = int(summary["non_compliant"] or 0)



    compliance_pct = round((compliant / total) * 100, 2) if total > 0 else 0



    epp_row = cur.execute(

        """

        SELECT

            COALESCE(SUM(missing_helmet_count), 0) AS casco,

            COALESCE(SUM(missing_gloves_count), 0) AS guantes,

            COALESCE(SUM(missing_goggles_count), 0) AS antiparras,

            COALESCE(SUM(missing_reflective_vest_count), 0) AS chaleco_reflectante,

            COALESCE(SUM(missing_mask_count), 0) AS mascarilla

        FROM epp_events

        WHERE timestamp >= datetime(?, ?)

        """,

        (latest, modifier),

    ).fetchone()



    missing_casco = int(epp_row["casco"] or 0)

    missing_guantes = int(epp_row["guantes"] or 0)

    missing_antiparras = int(epp_row["antiparras"] or 0)

    missing_chaleco = int(epp_row["chaleco_reflectante"] or 0)

    missing_mascarilla = int(epp_row["mascarilla"] or 0)



    def detected_pct(missing_count):

        if total <= 0:

            return 0

        return round(max(0, 100 - ((missing_count / total) * 100)), 2)




    epp_breakdown = [

        {

            "name": "Casco",

            "detected_pct": detected_pct(missing_casco),

        },

        {

            "name": "Chaleco reflectante",

            "detected_pct": detected_pct(missing_chaleco),

        },

        {

            "name": "Lentes / antiparras",

            "detected_pct": detected_pct(missing_antiparras),

        },

    ]



    missing_options = [

        ("Casco", missing_casco),

        ("Chaleco reflectante", missing_chaleco),

        ("Lentes / antiparras", missing_antiparras),

    ]



    most_missing_epp, most_missing_count = max(



        missing_options,

        key=lambda item: item[1],

    )



    alert = cur.execute(

        """

        SELECT alert_level, COUNT(*) AS total

        FROM epp_events

        WHERE timestamp >= datetime(?, ?)

          AND alert_level IS NOT NULL

          AND alert_level != ''

        GROUP BY alert_level

        ORDER BY total DESC

        LIMIT 1

        """,

        (latest, modifier),

    ).fetchone()



    conn.close()



    return {

        "window_minutes": minutes,

        "latest_timestamp": latest,

        "events_epp_evaluated": total,

        "events_compliant": compliant,

        "events_non_compliant": non_compliant,

        "compliance_observed_pct": compliance_pct,

        "most_missing_epp": most_missing_epp if most_missing_count > 0 else "-",

        "most_missing_epp_count": most_missing_count,

        "dominant_alert_level": alert["alert_level"] if alert else "-",

        "dominant_alert_count": int(alert["total"] or 0) if alert else 0,

        "epp_breakdown": epp_breakdown,

    }
