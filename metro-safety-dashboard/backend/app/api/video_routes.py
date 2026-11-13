import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.video_analysis import VideoAnalysis
from app.schemas.video_schema import VideoResult

router = APIRouter(prefix='/api/video-analyses', tags=['video-cycles'])


def verify_video_token(authorization: str | None = Header(default=None)):
    key = settings.VIDEO_INGEST_TOKEN
    if not key:
        raise HTTPException(503, 'Configure VIDEO_INGEST_TOKEN en el backend')
    supplied = (authorization or '').removeprefix('Bearer ')
    if not authorization or not authorization.startswith('Bearer ') or not secrets.compare_digest(supplied, key):
        raise HTTPException(401, 'Token de procesamiento inválido')


def video_cycle(row):
    p = row.payload
    origin = datetime.fromisoformat(p['recorded_at']) if p.get('recorded_at') else None
    def stamp(seconds):
        return (origin + timedelta(seconds=seconds)).isoformat() if origin else None
    stages = []
    for index, s in enumerate(p['segments']):
        stages.append({
            **s, 'id': f'{row.analysis_id}:{index}', 'sequence': index + 1,
            'started_at': stamp(s['start_seconds']), 'ended_at': stamp(s['end_seconds']),
            'duration_seconds': round(s['end_seconds'] - s['start_seconds'], 2),
            'target_duration_seconds': None, 'deviation_seconds': None,
            'status': 'UNOBSERVED' if s['observation'] == 'UNOBSERVED' else 'OBSERVED',
        })
    return {
        'id': row.analysis_id, 'analysis_id': row.analysis_id,
        'cycle_id': p.get('cycle_reference') or p['video_original'],
        'cycle_reference': p.get('cycle_reference'),
        'device_id': p['device_id'], 'front': p['front'], 'shift': p['shift'],
        'started_at': stamp(0), 'ended_at': stamp(p['duration_seconds']),
        'duration_seconds': p['duration_seconds'], 'target_duration_seconds': None,
        'deviation_seconds': None, 'advance_meters': None,
        'status': 'PARTIAL', 'source': 'VIDEO_PROCESADO',
        'video_original': p['video_original'], 'received_at': row.received_at.replace(tzinfo=timezone.utc).isoformat(),
        'model_classes': p['model_classes'], 'mapped_classes': p['mapped_classes'],
        'sample_seconds': p['sample_seconds'], 'warnings': p['warnings'], 'stages': stages,
    }


@router.post('', dependencies=[Depends(verify_video_token)])
def ingest(payload: VideoResult, db: Session = Depends(get_db)):
    existing = db.get(VideoAnalysis, payload.analysis_id)
    if existing:
        if existing.payload != payload.model_dump(mode='json'):
            raise HTTPException(409, 'analysis_id ya existe con otro contenido')
        return {'status': 'already_received', 'analysis_id': payload.analysis_id}
    row = VideoAnalysis(analysis_id=payload.analysis_id, payload=payload.model_dump(mode='json'))
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.get(VideoAnalysis, payload.analysis_id)
        if not existing or existing.payload != payload.model_dump(mode='json'):
            raise HTTPException(409, 'analysis_id ya existe con otro contenido')
        return {'status': 'already_received', 'analysis_id': payload.analysis_id}
    return {'status': 'received', 'analysis_id': row.analysis_id}


@router.get('')
def list_results(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    rows = db.query(VideoAnalysis).order_by(VideoAnalysis.received_at.desc()).limit(limit).all()
    return [video_cycle(row) for row in rows]


def grouped_video_cycles(rows):
    """Join only clips explicitly assigned to the same cycle and with recording dates."""
    import hashlib
    groups = {}
    independent = []
    for row in rows:
        cycle = video_cycle(row)
        if not cycle['cycle_reference'] or not cycle['started_at']:
            independent.append(cycle)
        else:
            key = (cycle['device_id'], cycle['front'], cycle['cycle_reference'])
            groups.setdefault(key, []).append(cycle)
    for key, clips in groups.items():
        clips.sort(key=lambda c: datetime.fromisoformat(c['started_at']))
        if len(clips) == 1:
            independent.extend(clips)
            continue
        if any(datetime.fromisoformat(a['ended_at']) > datetime.fromisoformat(b['started_at']) for a, b in zip(clips, clips[1:])):
            for clip in clips:
                clip['warnings'] = clip['warnings'] + ['Videos superpuestos en esta referencia; se mantienen separados para evitar sumar dos veces.']
            independent.extend(clips)
            continue
        first = datetime.fromisoformat(clips[0]['started_at'])
        combined = {**clips[0], 'analysis_id': 'group-' + hashlib.sha256('|'.join(key).encode()).hexdigest(),
            'video_original': ' + '.join(c['video_original'] for c in clips),
            'ended_at': clips[-1]['ended_at'], 'received_at': max(c['received_at'] for c in clips),
            'duration_seconds': (datetime.fromisoformat(clips[-1]['ended_at']) - first).total_seconds(),
            'model_classes': sorted({v for c in clips for v in c['model_classes']}),
            'mapped_classes': sorted({v for c in clips for v in c['mapped_classes']}),
            'warnings': sorted({w for c in clips for w in c['warnings']}) + ['Videos agrupados por referencia explícita; el ciclo continúa siendo parcial.'],
            'stages': []}
        cursor = 0
        for clip in clips:
            offset = (datetime.fromisoformat(clip['started_at']) - first).total_seconds()
            if offset > cursor:
                combined['stages'].append({'id': 'gap:' + str(cursor), 'stage_code': 'unobserved',
                    'stage_name': 'Sin grabación entre videos', 'start_seconds': cursor, 'end_seconds': offset,
                    'started_at': (first + timedelta(seconds=cursor)).isoformat(), 'ended_at': clip['started_at'],
                    'duration_seconds': offset - cursor, 'visible_seconds': 0, 'confidence': 0,
                    'observation': 'UNOBSERVED', 'status': 'UNOBSERVED', 'target_duration_seconds': None,
                    'deviation_seconds': None, 'tracked_object': ''})
            combined['stages'].extend([{**s, 'start_seconds': s['start_seconds'] + offset,
                'end_seconds': s['end_seconds'] + offset, 'video_original': clip['video_original']} for s in clip['stages']])
            cursor = offset + clip['duration_seconds']
        for sequence, stage in enumerate(combined['stages'], 1): stage['sequence'] = sequence
        independent.append(combined)
    return sorted(independent, key=lambda c: c['received_at'], reverse=True)
