# Dashboard Metro Línea 9

Conserva el módulo EPP y agrega el control del ciclo de excavación.

## Hitos

Excavación y perfilado; chequeo topográfico; sellado parcial; malla 1 y marcos; proyección HP1; mallas 2 y 3; salida de excavadora y cierre. En HP1 se mide el brazo, no el camión.

## Actualización en EC2

1. Actualizar el repositorio en la instancia.
2. Desde `backend`, activar el entorno virtual y reiniciar FastAPI. Al iniciar se crean `excavation_cycles` y `cycle_stages` sin eliminar los datos EPP.
3. Para una demostración inicial, ejecutar `python seed_linea9_demo.py`.
4. Copiar `frontend/` a `/var/www/metro-dashboard/` y recargar Nginx.

## API del modelo

- `POST /api/cycles`: crea un ciclo y sus hitos.
- `POST /api/cycles/{cycle_id}/stages`: agrega un hito.
- `GET /api/cycles/summary`: resumen y ciclo activo.
- `GET /api/cycles`: historial.

Para HP1 enviar `tracked_object: "brazo_hp1"` y `visible_seconds` con el tiempo acumulado del brazo visible.


## Recepción del ciclo por LoRaWAN

El gateway debe enviar los eventos al endpoint `POST /api/v1/lorawan/linea9-cycle` con el encabezado `Authorization: Bearer <token aceptado por la configuración vigente de LoRaWAN>`. El token no debe incluirse en el código del dashboard ni en el repositorio.

El cuerpo usa el formato de uplink Milesight y un objeto `object` con:

- `event_type`: `CYCLE_START`, `STAGE_START`, `STAGE_END` o `CYCLE_END`.
- `cycle_id`: identificador único del ciclo.
- En eventos de hito: `stage_code`, `stage_name` y `sequence`.
- `timestamp`: segundos Unix del evento (opcional; si falta, el backend usa la hora de recepción).
- `front`, `shift`, `cycle_target_duration_seconds`, `target_duration_seconds`, `duration_seconds` y `advance_meters`, cuando correspondan.

Secuencia esperada: `CYCLE_START`, pares `STAGE_START`/`STAGE_END` y finalmente `CYCLE_END`. La pantalla principal prioriza el estado del ciclo y conserva EPP como sección independiente. El estado de la API indica que el dashboard pudo consultar el backend; el estado LoRa muestra si existen eventos de ciclo, por lo que ambos indicadores no deben interpretarse como equivalentes.


Ejemplo mínimo de inicio de ciclo:

```json
{
  "event": "uplink",
  "devEUI": "A8404180C45D1554",
  "object": {
    "event_type": "CYCLE_START",
    "cycle_id": "L9-FN-20260930-001",
    "front": "Frente Norte",
    "shift": "Día",
    "cycle_target_duration_seconds": 17100
  }
}
```

Usar el `devEUI` autorizado en el backend y enviar las marcas de tiempo como Unix en segundos. Para una etapa, incluir también `stage_code`, `stage_name` y `sequence`.


## Identificación del origen de un ciclo

La tabla de ciclos también puede contener registros cargados manualmente o datos de demostración. Por eso, ver un ciclo en la pantalla no confirma por sí solo que llegó por LoRaWAN. El resumen muestra el identificador de ciclo y el dispositivo almacenado; valida el uplink en el servidor LoRaWAN y confirma que el `devEUI` autorizado coincide con `device_id` antes de considerar el dato real.
