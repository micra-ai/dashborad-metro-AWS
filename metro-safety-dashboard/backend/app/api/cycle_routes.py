from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.cycle_event import ExcavationCycle, CycleStage
from app.models.video_analysis import VideoAnalysis
from app.api.video_routes import grouped_video_cycles
from app.schemas.cycle_schema import CycleCreate, StageCreate

router = APIRouter(prefix="/api/cycles", tags=["excavation-cycle"])


def _iso(value):
    return value.isoformat() if value else None


def _duration(started_at, ended_at):
    if not started_at:
        return 0
    end = ended_at or datetime.utcnow()
    return max(0, int((end - started_at).total_seconds()))


def _stage_payload(stage):
    duration = _duration(stage.started_at, stage.ended_at)
    return {
        "id": stage.id,
        "stage_code": stage.stage_code,
        "stage_name": stage.stage_name,
        "sequence": stage.sequence,
        "started_at": _iso(stage.started_at),
        "ended_at": _iso(stage.ended_at),
        "duration_seconds": duration,
        "target_duration_seconds": stage.target_duration_seconds,
        "deviation_seconds": duration - stage.target_duration_seconds,
        "confidence": stage.confidence,
        "evidence_url": stage.evidence_url,
        "tracked_object": stage.tracked_object,
        "visible_seconds": stage.visible_seconds,
        "status": stage.status,
    }


def _cycle_payload(cycle, include_stages=True):
    duration = _duration(cycle.started_at, cycle.ended_at)
    data = {
        "source": "EVENTOS_API",
        "id": cycle.id,
        "cycle_id": cycle.cycle_id,
        "device_id": cycle.device_id,
        "front": cycle.front,
        "shift": cycle.shift,
        "started_at": _iso(cycle.started_at),
        "ended_at": _iso(cycle.ended_at),
        "duration_seconds": duration,
        "target_duration_seconds": cycle.target_duration_seconds,
        "deviation_seconds": duration - cycle.target_duration_seconds,
        "advance_meters": cycle.advance_meters,
        "status": cycle.status,
    }
    if include_stages:
        data["stages"] = [
            _stage_payload(stage)
            for stage in sorted(cycle.stages, key=lambda item: item.sequence)
        ]
    return data


@router.get("/summary")
def cycle_summary(db: Session = Depends(get_db)):
    test_cycle_ids = (

        "PRUEBA-LORA-20260930-01",

        "L9-DEMO-001",

        "L9-LORA-PRUEBA-001",

    )

    cycles = (

        db.query(ExcavationCycle)

        .filter(~ExcavationCycle.cycle_id.in_(test_cycle_ids))

        .order_by(ExcavationCycle.started_at.desc())

        .all()

    )
    active = next((cycle for cycle in cycles if cycle.status == "IN_PROGRESS"), None)
    finished = [cycle for cycle in cycles if cycle.status == "COMPLETED"]
    avg_duration = (
        round(sum(_duration(c.started_at, c.ended_at) for c in finished) / len(finished))
        if finished else 0
    )
    video_rows = db.query(VideoAnalysis).order_by(VideoAnalysis.received_at.desc()).limit(100).all()
    video_count = db.query(VideoAnalysis).count()
    return {
        "video_observations_total": video_count,
        "video_cycles": grouped_video_cycles(video_rows),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cycles_total": len(cycles),
        "cycles_completed": len(finished),
        "average_duration_seconds": avg_duration,
        "advance_meters": round(sum(c.advance_meters or 0 for c in cycles), 2),
        "active_cycle": _cycle_payload(active) if active else None,
        "latest_cycle": _cycle_payload(cycles[0]) if cycles else None,
        "recent_cycles": [_cycle_payload(cycle) for cycle in cycles[:10]],
    }


@router.get("")
def list_cycles(limit: int = 50, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 500))
    cycles = db.query(ExcavationCycle).order_by(ExcavationCycle.started_at.desc()).limit(limit).all()
    return [_cycle_payload(cycle) for cycle in cycles]


@router.post("", status_code=201)
def create_cycle(payload: CycleCreate, db: Session = Depends(get_db)):
    if db.query(ExcavationCycle).filter(ExcavationCycle.cycle_id == payload.cycle_id).first():
        raise HTTPException(status_code=409, detail="El ciclo ya existe")
    values = payload.model_dump(exclude={"stages"})
    cycle = ExcavationCycle(**values)
    db.add(cycle)
    db.flush()
    for stage in payload.stages:
        db.add(CycleStage(cycle_id=cycle.id, **stage.model_dump()))
    db.commit()
    db.refresh(cycle)
    return _cycle_payload(cycle)


@router.post("/{cycle_id}/stages", status_code=201)
def add_stage(cycle_id: str, payload: StageCreate, db: Session = Depends(get_db)):
    cycle = db.query(ExcavationCycle).filter(ExcavationCycle.cycle_id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Ciclo no encontrado")
    stage = CycleStage(cycle_id=cycle.id, **payload.model_dump())
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return _stage_payload(stage)


# Historial recibido: consulta de solo lectura sobre raw_events.
import base64
import io
import json
import math
import zipfile
from datetime import date, timedelta
from xml.sax.saxutils import escape
from sqlalchemy import text


def _history_data(db, date_from, date_to, stage, device_id):
    if date_to < date_from:
        raise HTTPException(422, "La fecha final debe ser igual o posterior a la inicial")
    if (date_to - date_from).days > 31:
        raise HTTPException(422, "Selecciona un rango de hasta 32 días")
    params = {"start": date_from.isoformat(),
              "end": (date_to + timedelta(days=1)).isoformat(), "device": device_id}
    rows = db.execute(text("""
        SELECT id, event_id, event_type, device_id, received_at,
               validation_status, raw_payload
        FROM raw_events
        WHERE received_at >= :start AND received_at < :end
          AND device_id = :device
          AND event_type IN ('CYCLE_START','CYCLE_END','STAGE_START','STAGE_END')
        ORDER BY received_at, id LIMIT 50001
    """), params).mappings().all()
    if len(rows) > 50000:
        raise HTTPException(413, "Demasiados mensajes. Reduce el rango de fechas")
    groups, last, originals = [], {}, []
    invalid = 0
    for row in rows:
        r = dict(row)
        try:
            payload = json.loads(r["raw_payload"])
            obj = payload.get("object") or {}
            if not isinstance(obj, dict):
                raise ValueError("object no es un objeto")
            stamp = datetime.fromisoformat(str(r["received_at"]).replace("Z", "+00:00"))
        except (ValueError, TypeError, AttributeError):
            invalid += 1
            originals.append(r)
            continue
        if stage and obj.get("stage_code") != stage:
            continue
        originals.append(r)
        key = (r["device_id"], r["event_type"], json.dumps(payload, sort_keys=True))
        prior = last.get(key)
        if prior is not None and 0 <= (stamp - prior["_first"]).total_seconds() <= 60:
            prior["message_count"] += 1
            prior["last_received_at"] = str(r["received_at"])
            continue
        dur = obj.get("duration_seconds")
        if isinstance(dur, bool) or not isinstance(dur, (float, int)) or not math.isfinite(dur) or dur < 0:
            dur = None
        item = {"source_id": r["id"], "event_type": r["event_type"],
                "cycle_id": obj.get("cycle_id"), "stage_code": obj.get("stage_code"),
                "stage_name": obj.get("stage_name"), "device_id": r["device_id"],
                "first_received_at": str(r["received_at"]),
                "last_received_at": str(r["received_at"]), "message_count": 1,
                "duration_seconds": dur, "confidence": obj.get("confidence"),
                "front": obj.get("front"), "shift": obj.get("shift"),
                "evidence_url": obj.get("evidence_url"),
                "inicio_evento": obj.get("inicio_evento"), "fin_evento": obj.get("fin_evento"),
                "estado_sello": obj.get("estado_sello"),
                "detected_stage_code": obj.get("detected_stage_code"),
                "classification_status": obj.get("classification_status"), "_first": stamp}
        groups.append(item)
        last[key] = item
    for item in groups:
        item.pop("_first")
    return groups, originals, invalid


def _history_xlsx(sheets):
    # XLSX estándar con strings inline: no requiere instalar librerías en AWS.
    def col(n):
        result = ""
        while n:
            n, v = divmod(n - 1, 26)
            result = chr(65 + v) + result
        return result
    def clean(value):
        return ''.join(c for c in str(value) if c in '\t\n\r' or 32 <= ord(c) <= 0xD7FF or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)
    buf = io.BytesIO()
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    rel = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        types = ''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,len(sheets)+1))
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+types+'</Types>')
        z.writestr('_rels/.rels', f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{rel}/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'+''.join(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>' for i,(name,_) in enumerate(sheets,1))+'</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="{rel}/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(sheets)+1))+f'<Relationship Id="rId{len(sheets)+1}" Type="{rel}/styles" Target="styles.xml"/></Relationships>')
        z.writestr('xl/styles.xml', f'<styleSheet xmlns="{ns}"><fonts count="2"><font><sz val="11"/><name val="Arial"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Arial"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF182B49"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="2"><xf fontId="0" fillId="0" borderId="0" xfId="0"/><xf fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
        for i, (name, rows) in enumerate(sheets,1):
            body = []
            for rn, row in enumerate(rows,1):
                cells=[]
                for cn,v in enumerate(row,1):
                    ref=f'{col(cn)}{rn}'; style=' s="1"' if rn==1 else ''
                    if v is None: continue
                    if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v):
                        cells.append(f'<c r="{ref}"{style}><v>{v}</v></c>')
                    else:
                        cells.append(f'<c r="{ref}" t="inlineStr"{style}><is><t xml:space="preserve">{escape(clean(v))}</t></is></c>')
                body.append(f'<row r="{rn}">'+''.join(cells)+'</row>')
            end=f'{col(len(rows[0]))}{len(rows)}'
            z.writestr(f'xl/worksheets/sheet{i}.xml', f'<worksheet xmlns="{ns}"><sheetViews><sheetView workbookViewId="0" showGridLines="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="{len(rows[0])}" width="26" customWidth="1"/></cols><sheetData>'+''.join(body)+f'</sheetData><autoFilter ref="A1:{end}"/></worksheet>')
    return buf.getvalue()


@router.get('/history')
def received_history(date_from: date, date_to: date, stage: str = '',
                     device_id: str = 'A8404180C45D1554', page: int = 1,
                     page_size: int = 50, db: Session = Depends(get_db)):
    if page < 1 or not 1 <= page_size <= 200:
        raise HTTPException(422, 'Paginación inválida')
    groups, originals, invalid = _history_data(db,date_from,date_to,stage,device_id)
    groups.reverse()
    offset=(page-1)*page_size
    return {"items":groups[offset:offset+page_size], "total":len(groups),
            "original_count":len(originals), "invalid_count":invalid,
            "page":page, "page_size":page_size,
            "note":"Horas de recepción del servidor sin conversión. Agrupación provisional por contenido idéntico en 60 s. No son horas originales de trabajo."}


@router.get('/history/export')
def export_received_history(date_from: date, date_to: date, stage: str = '',
                            device_id: str = 'A8404180C45D1554', db: Session = Depends(get_db)):
    groups, originals, invalid = _history_data(db,date_from,date_to,stage,device_id)
    headers=['ID fuente','Tipo','Ciclo','Etapa','Código','Primera recepción Chile','Última recepción Chile','Mensajes','Duración reportada (s)','Frente','Turno','Confianza','URL evidencia','Inicio evento (ISO 8601)','Fin evento (ISO 8601)','Estado sello al inicio','Actividad detectada','Clasificación']
    keys=['source_id','event_type','cycle_id','stage_name','stage_code','first_received_at','last_received_at','message_count','duration_seconds','front','shift','confidence','evidence_url','inicio_evento','fin_evento','estado_sello','detected_stage_code','classification_status']
    from datetime import datetime as DT, timezone as TZ

    from zoneinfo import ZoneInfo



    def chile_time(value):

        if not value:

            return None

        stamp = DT.fromisoformat(str(value).replace("Z", "+00:00"))

        if stamp.tzinfo is None:

            stamp = stamp.replace(tzinfo=TZ.utc)

        return stamp.astimezone(ZoneInfo("America/Santiago")).isoformat(timespec="seconds")



    history = [headers]

    for g in groups:

        item = dict(g)

        for field in ("first_received_at", "last_received_at"):

            item[field] = chile_time(item.get(field))

        history.append([item.get(k) for k in keys])
    rawkeys=['id','event_id','event_type','device_id','received_at','validation_status','raw_payload']
    raw=[rawkeys]+[[str(r.get(k)) if r.get(k) is not None else None for k in rawkeys] for r in originals]
    notes=[['Concepto','Detalle'],['Rango',f'{date_from} a {date_to}'],['Dispositivo',device_id],['Filtro etapa',stage or 'Todas'],['Mensajes originales',len(originals)],['Grupos provisionales',len(groups)],['Mensajes no interpretables',invalid],['Fechas','Historial: recepción convertida a America/Santiago con desfase explícito. Mensajes originales: datos de almacenamiento sin conversión. El rango de fechas corresponde a días de Chile.'],['Agrupación','Contenido completo idéntico dentro de 60 s desde el primero. Posibles repeticiones.'],['Duración','Reportada por el dispositivo; no se suma como tiempo total de trabajo.'],['Cierre','Los inicios no se emparejan automáticamente. Ausencia de CYCLE_END no acredita trabajo continuo.'],['Imágenes','Solo se incluyen URLs si fueron recibidas. Videos locales requieren procesamiento separado.']]
    content=_history_xlsx([('Historial',history),('Mensajes originales',raw),('Notas',notes)])
    return {'filename':f'historial-linea9-{date_from}-{date_to}.xlsx',
            'content_base64':base64.b64encode(content).decode('ascii')}
