import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.schemas.milesight_schema import MilesightUplinkPayload, DecodedObject
from app.api.milesight_routes import process_milesight_payload, verify_milesight_token
from fastapi import HTTPException

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = TestingSessionLocal()

def test_milesight_telemetry_valid():
    payload = MilesightUplinkPayload(
        event="uplink",
        devEUI="A8404180C45D1554",
        deviceName="LA66-Rocas-Pique1",
        applicationId="1",
        applicationName="Metro_Rocas",
        fPort=2,
        fCnt=128,
        rssi=-85,
        snr=8.5,
        data="05010096",
        object=DecodedObject(
            rocas_detectadas=5,
            deslizamientos=1,
            avance_metros=1.5
        ),
        timestamp=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    )
    
    result = process_milesight_payload(payload, db)
    assert result["status"] == "success"
    assert result["received_data"]["devEUI"] == "A8404180C45D1554"
    assert result["received_data"]["rocas_detectadas"] == 5
    assert result["received_data"]["deslizamientos"] == 1
    assert result["received_data"]["avance_metros"] == 1.5

def test_milesight_unauthorized_device():
    payload = MilesightUplinkPayload(
        devEUI="UNAUTHORIZED_9999",
        object=DecodedObject(rocas_detectadas=1, deslizamientos=0, avance_metros=0.5)
    )
    try:
        process_milesight_payload(payload, db)
        assert False, "Should have raised HTTPException 403"
    except HTTPException as e:
        assert e.status_code == 403

def test_milesight_token_verification():
    verify_milesight_token(authorization="Bearer EBR_Metro_Secret_Token_2026")

    try:
        verify_milesight_token(authorization="Bearer INVALID_TOKEN")
        assert False, "Should have raised 401"
    except HTTPException as e:
        assert e.status_code == 401

def test_milesight_hex_fallback():
    payload = MilesightUplinkPayload(
        devEUI="A8404180C45D1554",
        data="05010096"
    )
    result = process_milesight_payload(payload, db)
    assert result["status"] == "success"
    assert result["received_data"]["rocas_detectadas"] == 5
    assert result["received_data"]["deslizamientos"] == 1
    assert result["received_data"]["avance_metros"] == 1.5

def test_dashboard_excavation_online_offline_status():
    from app.services.dashboard_service import get_excavation_summary
    from app.models.excavation_event import ExcavationEvent
    
    db.query(ExcavationEvent).delete()
    db.commit()

    # 1. Send recent payload (within current time)
    now_ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    recent_payload = MilesightUplinkPayload(
        devEUI="A8404180C45D1554",
        object=DecodedObject(rocas_detectadas=8, deslizamientos=2, avance_metros=3.2),
        timestamp=now_ts
    )
    process_milesight_payload(recent_payload, db)
    
    summary = get_excavation_summary(db)
    assert summary.device_status == "Online"
    assert summary.rocas_detectadas == 8
    assert summary.deslizamientos == 2
    assert summary.avance_metros == 3.2

    # 2. Test Offline when event timestamp is older than 15 minutes (20 minutes ago)
    old_ts = now_ts - 1200 # 20 minutes ago
    old_payload = MilesightUplinkPayload(
        devEUI="A8404180C45D1554",
        object=DecodedObject(rocas_detectadas=10, deslizamientos=0, avance_metros=4.0),
        timestamp=old_ts
    )
    # Clear table to test single old event
    from app.models.excavation_event import ExcavationEvent
    db.query(ExcavationEvent).delete()
    db.commit()

    process_milesight_payload(old_payload, db)
    summary_old = get_excavation_summary(db)
    assert summary_old.device_status == "Offline"
    assert summary_old.rocas_detectadas == 10
    assert summary_old.deslizamientos == 0
    assert summary_old.avance_metros == 4.0

