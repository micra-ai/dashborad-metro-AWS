from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
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
