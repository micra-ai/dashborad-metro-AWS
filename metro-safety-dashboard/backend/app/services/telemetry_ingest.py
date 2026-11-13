"""Atomic persistence and idempotency; existing database tables remain unchanged."""
import hashlib
import json
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.raw_event import RawEvent


def utc_naive(value):
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def stable_key(namespace, device_id, event_id):
    value = json.dumps([namespace, device_id, event_id], ensure_ascii=False)
    return "ingest_" + hashlib.sha256(value.encode()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def persist(db, *, namespace, device_id, event_id, event_type, incoming, stored, build_row):
    key = stable_key(namespace, device_id, event_id)
    fingerprint = hashlib.sha256(canonical(incoming).encode()).hexdigest()

    def duplicate(existing):
        saved = json.loads(existing.raw_payload)
        if saved.get("ingest_fingerprint") != fingerprint:
            raise HTTPException(409, "event_id ya utilizado con contenido diferente")
        return existing, True

    existing = db.query(RawEvent).filter(RawEvent.event_id == key).first()
    if existing:
        return duplicate(existing)
    stored = dict(stored, ingest_fingerprint=fingerprint)
    raw = RawEvent(event_id=key, event_type=event_type,
                   schema_version="4.0" if namespace == "construction" else "sensor-1.0",
                   device_id=device_id, received_at=datetime.now(timezone.utc).replace(tzinfo=None),
                   raw_payload=json.dumps(stored, ensure_ascii=False), validation_status="VALID")
    try:
        db.add(raw)
        db.flush()
        db.add(build_row(raw.id))
        db.commit()
        return raw, False
    except IntegrityError:
        db.rollback()
        # Another request may have committed the same event concurrently.
        existing = db.query(RawEvent).filter(RawEvent.event_id == key).first()
        if existing:
            return duplicate(existing)
        raise
    except Exception:
        db.rollback()
        raise
