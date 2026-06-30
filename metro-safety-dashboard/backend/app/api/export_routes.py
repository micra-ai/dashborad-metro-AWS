from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io
from app.database.session import get_db
from app.models.raw_event import RawEvent
from app.models.epp_event import EppEvent
from app.auth.routes import get_current_user

router = APIRouter(prefix="/api/export", tags=["export"], dependencies=[Depends(get_current_user)])

@router.get("/csv")
def export_csv(
    event_type: Optional[str] = None,
    device_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RawEvent)
    if event_type:
        query = query.filter(RawEvent.event_type == event_type)
    if device_id:
        query = query.filter(RawEvent.device_id == device_id)
    if start_date:
        query = query.filter(RawEvent.received_at >= start_date)
    if end_date:
        query = query.filter(RawEvent.received_at <= end_date)
    
    events = query.order_by(RawEvent.received_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "event_id", "event_type", "device_id", "received_at", "validation_status"])
    for event in events:
        writer.writerow([event.id, event.event_id, event.event_type, event.device_id, event.received_at.isoformat(), event.validation_status])
        
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=events.csv"
    return response





@router.get("/alerts-csv")

def export_alerts_csv(

    device_id: Optional[str] = None,

    start_date: Optional[str] = None,

    end_date: Optional[str] = None,

    limit: int = 5000,

    db: Session = Depends(get_db),

):

    from sqlalchemy import or_



    safe_limit = max(1, min(limit, 10000))



    query = db.query(EppEvent).filter(

        or_(

            EppEvent.missing_helmet_count > 0,

            EppEvent.missing_reflective_vest_count > 0,

            EppEvent.missing_goggles_count > 0,

        )

    )



    if device_id:

        query = query.filter(EppEvent.device_id == device_id)



    if start_date:

        query = query.filter(EppEvent.timestamp >= start_date)



    if end_date:

        query = query.filter(EppEvent.timestamp <= end_date)



    events = (

        query

        .order_by(EppEvent.timestamp.desc())

        .limit(safe_limit)

        .all()

    )



    output = io.StringIO()

    writer = csv.writer(output)



    writer.writerow([

        "event_id",

        "fecha",

        "dispositivo",

        "sitio",

        "area",

        "zona",

        "trabajadores_detectados",

        "falta_casco",

        "falta_chaleco_reflectante",

        "falta_lentes",

        "elementos_faltantes",

        "porcentaje_cumplimiento",

        "nivel_alerta",

        "imagen_url",

    ])



    for event in events:

        missing = []



        if (event.missing_helmet_count or 0) > 0:

            missing.append("Casco")



        if (event.missing_reflective_vest_count or 0) > 0:

            missing.append("Chaleco reflectante")



        if (event.missing_goggles_count or 0) > 0:

            missing.append("Lentes")



        writer.writerow([

            event.event_id,

            event.timestamp.isoformat() if event.timestamp else "",

            event.device_id or "",

            event.site or "",

            event.area or "",

            event.zone or "",

            event.workers_detected or 0,

            event.missing_helmet_count or 0,

            event.missing_reflective_vest_count or 0,

            event.missing_goggles_count or 0,

            ", ".join(missing),

            event.overall_compliance_percentage or 0,

            event.alert_level or "",

            event.image_url or "",

        ])



    response = Response(

        content="\\ufeff" + output.getvalue(),

        media_type="text/csv; charset=utf-8",

    )

    response.headers["Content-Disposition"] = (

        'attachment; filename="alertas_epp.csv"'

    )

    return response

