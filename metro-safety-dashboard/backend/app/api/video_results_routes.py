import json

from pathlib import Path



from fastapi import APIRouter, Depends, HTTPException

from app.auth.routes import get_current_user



router = APIRouter(

    prefix="/api/video-results",

    tags=["videos-procesados"],

)



RESULTS_DIR = (

    Path(__file__).resolve().parents[2]

    / "data"

    / "videos_procesados"

)





@router.get("")

def list_video_results(current_user=Depends(get_current_user)):

    if not current_user.is_active:

        raise HTTPException(

            status_code=403,

            detail="Cuenta desactivada",

        )



    registros = []



    for archivo in sorted(RESULTS_DIR.glob("*.json")):

        try:

            with archivo.open("r", encoding="utf-8-sig") as contenido:

                registro = json.load(contenido)



            if not isinstance(registro, dict):

                raise ValueError("El registro debe ser un objeto JSON")



            registros.append(registro)



        except (OSError, ValueError) as error:

            raise HTTPException(

                status_code=500,

                detail=f"No se pudo leer el registro {archivo.name}",

            ) from error



    return {

        "fuente": "VIDEO_PROCESADO",

        "registros_total": len(registros),

        "registros": registros,

    }
