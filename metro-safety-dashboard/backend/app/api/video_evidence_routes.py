"""Independent evidence storage: analysis payloads and cycle times remain immutable."""
import base64
import binascii
import hashlib
import json
import math
import re
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.video_analysis import VideoAnalysis
from app.api.video_routes import verify_video_token

router = APIRouter(prefix='/api/video-analyses', tags=['video-evidence'])
STORE = Path(__file__).resolve().parents[2] / 'video_evidence'
MAX_BODY = 3_000_000


def segment_for(db, analysis_id, index):
    if not re.fullmatch(r'[a-f0-9]{64}', analysis_id):
        raise HTTPException(404, 'Análisis no encontrado')
    row = db.get(VideoAnalysis, analysis_id)
    if row is None or index < 0 or index >= len(row.payload['segments']):
        raise HTTPException(404, 'Intervalo no encontrado')
    segment = row.payload['segments'][index]
    if segment['observation'] == 'UNOBSERVED':
        raise HTTPException(422, 'Un tramo sin detección no admite evidencia de tarea')
    return segment


@router.post('/{analysis_id}/evidence/{index}', dependencies=[Depends(verify_video_token)])
async def upload(analysis_id: str, index: int, request: Request, db: Session = Depends(get_db)):
    segment = segment_for(db, analysis_id, index)
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BODY:
            raise HTTPException(413, 'Imagen demasiado grande')
    try:
        value = json.loads(body)
        timestamp = float(value['timestamp_seconds'])
        confidence = float(value['confidence'])
        class_name = value['class_name']
        raw = base64.b64decode(value['jpeg_base64'], validate=True)
        valid = (math.isfinite(timestamp) and segment['start_seconds'] <= timestamp < segment['end_seconds']
                 and math.isfinite(confidence) and 0 < confidence <= 1
                 and class_name == segment['tracked_object']
                 and raw.startswith(b'\xff\xd8\xff') and raw.endswith(b'\xff\xd9')
                 and 100 <= len(raw) <= 2_000_000)
        if not valid:
            raise ValueError('Evidencia fuera del intervalo, clase distinta o JPEG inválido')
    except (KeyError, TypeError, ValueError, binascii.Error) as error:
        raise HTTPException(422, 'Evidencia inválida') from error
    directory = STORE / analysis_id
    directory.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw).hexdigest()
    image_path = directory / f'{index}-{digest}.jpg'
    if not image_path.exists():
        temp = directory / (uuid.uuid4().hex + '.tmp')
        try:
            temp.write_bytes(raw)
            temp.replace(image_path)
        finally:
            temp.unlink(missing_ok=True)
    metadata = {'segment_index': index, 'timestamp_seconds': timestamp, 'confidence': confidence,
                'class_name': class_name, 'sha256': digest,
                'image_url': f'/api/video-analyses/{analysis_id}/evidence/{index}/image?v={digest}'}
    temp = directory / (uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps(metadata), encoding='utf-8')
        temp.replace(directory / f'{index}.json')
    finally:
        temp.unlink(missing_ok=True)
    return {'status': 'received', **metadata}


@router.get('/{analysis_id}/evidence')
def listing(analysis_id: str, db: Session = Depends(get_db)):
    if not re.fullmatch(r'[a-f0-9]{64}', analysis_id) or db.get(VideoAnalysis, analysis_id) is None:
        raise HTTPException(404, 'Análisis no encontrado')
    directory = STORE / analysis_id
    items = []
    for path in directory.glob('*.json'):
        try:
            items.append(json.loads(path.read_text(encoding='utf-8')))
        except (ValueError, OSError):
            continue
    return {'analysis_id': analysis_id, 'items': sorted(items, key=lambda x: x['segment_index'])}


@router.get('/{analysis_id}/evidence/{index}/image')
def image(analysis_id: str, index: int, db: Session = Depends(get_db)):
    segment_for(db, analysis_id, index)
    path = STORE / analysis_id / f'{index}.json'
    if not path.exists():
        raise HTTPException(404, 'Foto pendiente')
    metadata = json.loads(path.read_text(encoding='utf-8'))
    raw_path = path.parent / f"{index}-{metadata['sha256']}.jpg"
    if not raw_path.exists():
        raise HTTPException(404, 'Foto pendiente')
    return FileResponse(raw_path, media_type='image/jpeg', headers={'Cache-Control': 'no-cache',
        'X-Content-Type-Options': 'nosniff'})
