from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import get_db
from app.models.epp_event import EppEvent
from app.services.dashboard_service import get_dashboard_summary, get_epp_summary, get_excavation_summary, get_latest_images
from app.auth.routes import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)

@router.get("/epp")
def get_epp(db: Session = Depends(get_db)):
    return get_epp_summary(db)

@router.get("/excavation")
def get_excavation(db: Session = Depends(get_db)):
    return get_excavation_summary(db)

@router.get("/latest-images")
def get_latest_images_route(limit: int = 5, db: Session = Depends(get_db)):
    return get_latest_images(db, limit)




@router.get("/epp-alerts")

def get_epp_alerts(

    limit: int = 100,

    device_id: str | None = None,

    db: Session = Depends(get_db),

):

    """

    Devuelve únicamente alertas asociadas a los EPP utilizados por Metro:

    casco, chaleco reflectante y lentes.

    """



    safe_limit = max(1, min(limit, 500))



    query = db.query(EppEvent).filter(

        or_(

            EppEvent.missing_helmet_count > 0,

            EppEvent.missing_reflective_vest_count > 0,

            EppEvent.missing_goggles_count > 0,

        )

    )



    if device_id:

        query = query.filter(EppEvent.device_id == device_id)



    events = (

        query

        .order_by(EppEvent.timestamp.desc())

        .limit(safe_limit)

        .all()

    )



    results = []



    for event in events:

        missing_items = []



        if (event.missing_helmet_count or 0) > 0:

            missing_items.append("Casco")



        if (event.missing_reflective_vest_count or 0) > 0:

            missing_items.append("Chaleco reflectante")



        if (event.missing_goggles_count or 0) > 0:

            missing_items.append("Lentes")



        results.append({

            "event_id": event.event_id,

            "device_id": event.device_id,

            "timestamp": (

                event.timestamp.isoformat()

                if event.timestamp

                else None

            ),

            "site": event.site,

            "area": event.area,

            "zone": event.zone,

            "workers_detected": event.workers_detected or 0,

            "missing_helmet_count": event.missing_helmet_count or 0,

            "missing_reflective_vest_count": (

                event.missing_reflective_vest_count or 0

            ),

            "missing_goggles_count": event.missing_goggles_count or 0,

            "missing_items": missing_items,

            "missing_summary": ", ".join(missing_items),

            "overall_compliance_percentage": (

                event.overall_compliance_percentage or 0

            ),

            "alert_level": event.alert_level or "INFO",

            "image_url": event.image_url,

        })



    return {

        "total": len(results),

        "alerts": results,

    }

