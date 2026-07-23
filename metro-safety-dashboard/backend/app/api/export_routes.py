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






@router.get("/alerts-xlsx")

def export_alerts_xlsx(

    device_id: Optional[str] = None,

    limit: int = 2000,

    db: Session = Depends(get_db),

):

    import io

    import xlsxwriter

    from sqlalchemy import or_



    # Protección para no volver a saturar la instancia.

    safe_limit = max(1, min(limit, 5000))



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



    output = io.BytesIO()



    workbook = xlsxwriter.Workbook(

        output,

        {

            "in_memory": True,

            "constant_memory": True,

        },

    )



    worksheet = workbook.add_worksheet("Alertas EPP")

    worksheet.freeze_panes(1, 0)

    worksheet.autofilter(0, 0, max(len(events), 1), 13)



    title_format = workbook.add_format({

        "bold": True,

        "font_color": "#FFFFFF",

        "bg_color": "#1E293B",

        "border": 1,

        "align": "center",

        "valign": "vcenter",

        "text_wrap": True,

    })



    normal_format = workbook.add_format({

        "border": 1,

        "border_color": "#CBD5E1",

        "valign": "top",

    })



    center_format = workbook.add_format({

        "border": 1,

        "border_color": "#CBD5E1",

        "align": "center",

        "valign": "vcenter",

    })



    date_format = workbook.add_format({

        "border": 1,

        "border_color": "#CBD5E1",

        "num_format": "dd-mm-yyyy hh:mm:ss",

    })



    high_format = workbook.add_format({

        "bold": True,

        "font_color": "#FFFFFF",

        "bg_color": "#DC2626",

        "border": 1,

        "align": "center",

    })



    medium_format = workbook.add_format({

        "bold": True,

        "font_color": "#111827",

        "bg_color": "#F59E0B",

        "border": 1,

        "align": "center",

    })



    low_format = workbook.add_format({

        "bold": True,

        "font_color": "#111827",

        "bg_color": "#FDE047",

        "border": 1,

        "align": "center",

    })



    link_format = workbook.add_format({

        "font_color": "#0563C1",

        "underline": True,

        "border": 1,

        "align": "center",

    })



    headers = [

        "Fecha",

        "Dispositivo",

        "Sitio",

        "Área",

        "Zona",

        "Trabajadores detectados",

        "Falta casco",

        "Falta chaleco reflectante",

        "Falta lentes",

        "Elementos faltantes",

        "Cumplimiento (%)",

        "Nivel de alerta",

        "Evidencia",

        "ID Evento",

    ]



    for col, header in enumerate(headers):

        worksheet.write(0, col, header, title_format)



    worksheet.set_row(0, 34)



    widths = [

        21, 14, 18, 22, 28, 20, 13,

        24, 13, 38, 18, 16, 16, 39,

    ]



    for col, width in enumerate(widths):

        worksheet.set_column(col, col, width)



    for row_index, event in enumerate(events, start=1):

        missing = []



        if (event.missing_helmet_count or 0) > 0:

            missing.append("Casco")



        if (event.missing_reflective_vest_count or 0) > 0:

            missing.append("Chaleco reflectante")



        if (event.missing_goggles_count or 0) > 0:

            missing.append("Lentes")



        worksheet.write_datetime(

            row_index,

            0,

            event.timestamp,

            date_format,

        ) if event.timestamp else worksheet.write(

            row_index, 0, "", normal_format

        )



        worksheet.write(row_index, 1, event.device_id or "", normal_format)

        worksheet.write(row_index, 2, event.site or "", normal_format)

        worksheet.write(row_index, 3, event.area or "", normal_format)

        worksheet.write(row_index, 4, event.zone or "", normal_format)



        worksheet.write_number(

            row_index, 5, event.workers_detected or 0, center_format

        )

        worksheet.write_number(

            row_index, 6, event.missing_helmet_count or 0, center_format

        )

        worksheet.write_number(

            row_index,

            7,

            event.missing_reflective_vest_count or 0,

            center_format,

        )

        worksheet.write_number(

            row_index, 8, event.missing_goggles_count or 0, center_format

        )



        worksheet.write(

            row_index, 9, ", ".join(missing), normal_format

        )



        worksheet.write_number(

            row_index,

            10,

            event.overall_compliance_percentage or 0,

            center_format,

        )



        alert_level = (event.alert_level or "INFO").upper()



        if alert_level == "HIGH":

            level_format = high_format

        elif alert_level == "MEDIUM":

            level_format = medium_format

        elif alert_level == "LOW":

            level_format = low_format

        else:

            level_format = center_format



        worksheet.write(row_index, 11, alert_level, level_format)



        if event.image_url:

            image_url = event.image_url



            if image_url.startswith("/"):

                image_url = (

                    "https://100-29-228-117.sslip.io"

                    + image_url

                )



            worksheet.write_url(

                row_index,

                12,

                image_url,

                link_format,

                "Ver imagen",

            )

        else:

            worksheet.write(

                row_index, 12, "Sin imagen", center_format

            )



        worksheet.write(

            row_index, 13, event.event_id or "", normal_format

        )



    # Color visual para incumplimientos.

    if events:

        worksheet.conditional_format(

            1,

            6,

            len(events),

            8,

            {

                "type": "cell",

                "criteria": ">",

                "value": 0,

                "format": workbook.add_format({

                    "bg_color": "#FECACA",

                    "font_color": "#991B1B",

                    "bold": True,

                    "border": 1,

                    "align": "center",

                }),

            },

        )



    workbook.close()

    output.seek(0)



    return Response(

        content=output.getvalue(),

        media_type=(

            "application/vnd.openxmlformats-officedocument."

            "spreadsheetml.sheet"

        ),

        headers={

            "Content-Disposition": (

                'attachment; filename="alertas_epp.xlsx"'

            )

        },

    )






@router.get("/alerts-with-images-xlsx")

def export_alerts_with_images_xlsx(

    limit: int = 100,

    db: Session = Depends(get_db),

):

    from pathlib import Path

    import io

    import xlsxwriter

    from sqlalchemy import or_



    safe_limit = max(1, min(limit, 200))



    events = (

        db.query(EppEvent)

        .filter(

            or_(

                EppEvent.missing_helmet_count > 0,

                EppEvent.missing_reflective_vest_count > 0,

                EppEvent.missing_goggles_count > 0,

            ),

            EppEvent.image_url.isnot(None),

            EppEvent.image_url != "",

        )

        .order_by(EppEvent.timestamp.desc())

        .limit(safe_limit)

        .all()

    )



    backend_dir = Path(__file__).resolve().parents[2]

    images_dir = backend_dir / "static" / "images"



    output = io.BytesIO()

    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    sheet = workbook.add_worksheet("Alertas con evidencia")



    header = workbook.add_format({

        "bold": True,

        "font_color": "#FFFFFF",

        "bg_color": "#1E293B",

        "border": 1,

        "align": "center",

        "valign": "vcenter",

        "text_wrap": True,

    })



    normal = workbook.add_format({

        "border": 1,

        "valign": "vcenter",

    })



    center = workbook.add_format({

        "border": 1,

        "align": "center",

        "valign": "vcenter",

    })



    high = workbook.add_format({

        "bold": True,

        "font_color": "#FFFFFF",

        "bg_color": "#DC2626",

        "border": 1,

        "align": "center",

        "valign": "vcenter",

    })



    headers = [

        "Fecha",

        "Dispositivo",

        "Trabajadores",

        "Falta casco",

        "Falta chaleco",

        "Falta lentes",

        "Elementos faltantes",

        "Nivel",

        "Evidencia",

        "ID Evento",

    ]



    for col, value in enumerate(headers):

        sheet.write(0, col, value, header)



    widths = [21, 14, 14, 13, 16, 13, 36, 13, 28, 39]



    for col, width in enumerate(widths):

        sheet.set_column(col, col, width)



    sheet.set_row(0, 34)

    sheet.freeze_panes(1, 0)

    sheet.autofilter(0, 0, max(len(events), 1), len(headers) - 1)



    for row, event in enumerate(events, start=1):

        missing = []



        if (event.missing_helmet_count or 0) > 0:

            missing.append("Casco")



        if (event.missing_reflective_vest_count or 0) > 0:

            missing.append("Chaleco reflectante")



        if (event.missing_goggles_count or 0) > 0:

            missing.append("Lentes")



        sheet.set_row(row, 90)



        sheet.write(

            row,

            0,

            event.timestamp.isoformat() if event.timestamp else "",

            normal,

        )

        sheet.write(row, 1, event.device_id or "", normal)

        sheet.write_number(row, 2, event.workers_detected or 0, center)

        sheet.write_number(row, 3, event.missing_helmet_count or 0, center)

        sheet.write_number(

            row,

            4,

            event.missing_reflective_vest_count or 0,

            center,

        )

        sheet.write_number(row, 5, event.missing_goggles_count or 0, center)

        sheet.write(row, 6, ", ".join(missing), normal)

        sheet.write(row, 7, event.alert_level or "HIGH", high)

        sheet.write(row, 9, event.event_id or "", normal)



        filename = Path(event.image_url).name

        image_path = images_dir / filename



        if image_path.exists():

            sheet.insert_image(

                row,

                8,

                str(image_path),

                {

                    "x_scale": 0.23,

                    "y_scale": 0.23,

                    "x_offset": 5,

                    "y_offset": 5,

                    "object_position": 1,

                },

            )

        else:

            sheet.write(row, 8, "Imagen no encontrada", center)



    workbook.close()

    output.seek(0)



    return Response(

        content=output.getvalue(),

        media_type=(

            "application/vnd.openxmlformats-officedocument."

            "spreadsheetml.sheet"

        ),

        headers={

            "Content-Disposition": (

                'attachment; filename="alertas_epp_con_imagenes.xlsx"'

            )

        },

    )

