import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.connection import Base
from app.database.session import get_db
from app.config import settings
from app.api.sensor_routes import router as sensor_router
from app.api.cycle_lora_routes import router as cycle_router
from app.api.milesight_routes import TOKEN_SECRETO
from app.models.raw_event import RawEvent
from app.models.telemetry import ConstructionActivity, SensorReading
from app.models.cycle_event import ExcavationCycle

CYCLE = "/api/v1/lorawan/linea9-cycle"
AUTH = {"Authorization": "Bearer " + TOKEN_SECRETO}
SENSOR_AUTH = {"Authorization": "Bearer test-only-sensor-token"}


def activity(**changes):
    obj = {"event_id": "evt-001", "event_type": "STAGE_END", "cycle_id": "cycle-001",
           "stage_code": "shotcrete", "inicio_evento": "2026-11-12T23:30:00-03:00",
           "fin_evento": "2026-11-13T00:30:00-03:00", "duration_seconds": 3600,
           "estado_sello": "sin_aplicar"}
    obj.update(changes)
    return {"devEUI": "A8404180C45D1554", "object": obj}


def reading(**changes):
    obj = {"event_id": "s-001", "device_id": "SENSOR-INT-001",
           "measured_at": "2026-11-12T13:00:00-03:00", "temperature_c": 18.2, "co2_ppm": 850}
    obj.update(changes)
    return obj


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setattr(settings, "SENSOR_INGEST_TOKEN", "test-only-sensor-token")
    monkeypatch.setattr(settings, "SENSOR_EXTERIOR_DEVICES", "SENSOR-EXT-001")
    monkeypatch.setattr(settings, "SENSOR_INTERIOR_DEVICES", "SENSOR-INT-001")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    app = FastAPI()
    app.include_router(sensor_router)
    app.include_router(cycle_router)
    def override_db():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        yield client, factory
    engine.dispose()


@pytest.mark.parametrize("seal,code,state", [
    ("sin_aplicar", "partial_seal", "CLASSIFIED"),
    ("aplicado", "hp1", "CLASSIFIED"), ("desconocido", "shotcrete", "PENDING")])
def test_classification_and_storage(env, seal, code, state):
    c, factory = env
    response = c.post(CYCLE, json=activity(estado_sello=seal), headers=AUTH)
    assert response.status_code == 201, response.text
    assert response.json()["stage_code"] == code
    assert response.json()["classification_status"] == state
    with factory() as db:
        row = db.query(ConstructionActivity).one()
        assert row.started_at.isoformat() == "2026-11-13T02:30:00"
        assert row.ended_at.isoformat() == "2026-11-13T03:30:00"
        payload = json.loads(db.query(RawEvent).one().raw_payload)
        assert payload["received_object"]["stage_code"] == "shotcrete"
        assert payload["object"]["stage_code"] == code
    out = c.get("/api/v1/lorawan/linea9-construction-events", headers=AUTH).json()
    assert out["events"][0]["stage_code"] == code
    assert c.get("/api/v1/lorawan/linea9-status").json()["latest_event"]["object"]["stage_code"] == code


@pytest.mark.parametrize("code", ["excavation", "topography", "mesh_frames"])
def test_other_activity_unchanged(env, code):
    c, _ = env
    assert c.post(CYCLE, json=activity(stage_code=code), headers=AUTH).json()["stage_code"] == code


def test_idempotency_conflict_and_radio_retry(env):
    c, factory = env
    p = activity()
    assert c.post(CYCLE, json=p, headers=AUTH).status_code == 201
    p.update(fCnt=55, rssi=-90)
    repeat = c.post(CYCLE, json=p, headers=AUTH)
    assert repeat.status_code == 200 and repeat.json()["duplicate"]
    assert c.post(CYCLE, json=activity(estado_sello="aplicado"), headers=AUTH).status_code == 409
    with factory() as db:
        assert db.query(RawEvent).count() == db.query(ConstructionActivity).count() == 1


@pytest.mark.parametrize("changes", [
    {"duration_seconds": 20}, {"fin_evento": "2026-11-12T20:00:00-03:00"},
    {"inicio_evento": "2026-11-12T23:30:00"}, {"estado_sello": "otro"},
    {"event_id": " "}, {"event_id": None}, {"stage_code": "hp1"},
    {"event_type": "STAGE_START"}, {"duration_seconds": None}])
def test_invalid_activity_no_partial_writes(env, changes):
    c, factory = env
    assert c.post(CYCLE, json=activity(**changes), headers=AUTH).status_code == 422
    with factory() as db:
        assert db.query(RawEvent).count() == 0


def test_flat_new_payload(env):
    c, _ = env
    p = activity()
    assert c.post(CYCLE, json={"devEUI": p["devEUI"], **p["object"]}, headers=AUTH).status_code == 201


def test_legacy_messages(env):
    c, factory = env
    for event_type in ["HEARTBEAT_STATUS", "STAGE_START", "STAGE_END", "CYCLE_START", "CYCLE_END"]:
        p = {"devEUI": "A8404180C45D1554", "object": {
            "event_type": event_type, "cycle_id": "legacy", "stage_code": "excavation"}}
        assert c.post(CYCLE, json=p, headers=AUTH).status_code == 201
    with factory() as db:
        assert db.query(RawEvent).count() == 5
        assert db.query(ExcavationCycle).one().status == "COMPLETED"
        assert db.query(ConstructionActivity).count() == 0


def test_cycle_auth_and_devices(env):
    c, _ = env
    assert c.post(CYCLE, json=activity()).status_code == 401
    p = activity(); p["devEUI"] = "UNKNOWN"
    assert c.post(CYCLE, json=p, headers=AUTH).status_code == 403
    assert c.get("/api/v1/lorawan/linea9-construction-events").status_code == 401


def test_sensor_endpoints_queries_and_retries(env):
    c, factory = env
    p = reading()
    assert c.post("/api/v1/sensors/interior", json=p, headers=SENSOR_AUTH).status_code == 201
    assert c.post("/api/v1/sensors/interior", json=p, headers=SENSOR_AUTH).status_code == 200
    assert c.post("/api/v1/sensors/interior", json=reading(co2_ppm=900), headers=SENSOR_AUTH).status_code == 409
    exterior = reading(device_id="sensor-ext-001"); exterior.pop("co2_ppm")
    assert c.post("/api/v1/sensors/exterior", json=exterior, headers=SENSOR_AUTH).status_code == 201
    out = c.get("/api/v1/sensors/readings?location=interior", headers=SENSOR_AUTH).json()
    assert out["readings"][0]["co2_ppm"] == 850
    assert out["readings"][0]["measured_at"] == "2026-11-12T16:00:00Z"
    with factory() as db:
        assert db.query(SensorReading).count() == db.query(RawEvent).count() == 2


@pytest.mark.parametrize("changes", [{"co2_ppm": -1}, {"co2_ppm": None},
    {"temperature_c": 200}, {"measured_at": "2026-11-12T13:00:00"}, {"unexpected": 1}])
def test_invalid_sensor(env, changes):
    c, _ = env
    assert c.post("/api/v1/sensors/interior", json=reading(**changes), headers=SENSOR_AUTH).status_code == 422


def test_sensor_permissions_and_config(env, monkeypatch):
    c, _ = env
    url = "/api/v1/sensors/interior"
    assert c.post(url, json=reading()).status_code == 401
    assert c.post(url, json=reading(device_id="SENSOR-EXT-001"), headers=SENSOR_AUTH).status_code == 403
    monkeypatch.setattr(settings, "SENSOR_INGEST_TOKEN", "")
    assert c.post(url, json=reading(), headers=SENSOR_AUTH).status_code == 503


def test_missing_co2_and_unexpected_exterior_co2(env):
    c, _ = env
    p = reading(); p.pop("co2_ppm")
    assert c.post("/api/v1/sensors/interior", json=p, headers=SENSOR_AUTH).status_code == 422
    assert c.post("/api/v1/sensors/exterior", json=reading(device_id="SENSOR-EXT-001"), headers=SENSOR_AUTH).status_code == 422


def test_history_contains_new_fields(env):
    from datetime import date
    from app.api.cycle_routes import _history_data
    c, factory = env
    c.post(CYCLE, json=activity(), headers=AUTH)
    with factory() as db:
        today = db.query(RawEvent).one().received_at.date()
        rows, originals, invalid = _history_data(db, today, today, "", "A8404180C45D1554")
        assert rows[0]["estado_sello"] == "sin_aplicar"
        assert rows[0]["stage_code"] == "partial_seal"
        assert rows[0]["inicio_evento"].endswith("-03:00")
