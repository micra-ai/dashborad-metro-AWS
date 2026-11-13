# Contrato de integración Línea 9 — versión 1

Estado: implementado y probado localmente. Pendiente de instalación y configuración en AWS.
El equipo emisor debe ajustarse a este contrato. No requiere acceso del dashboard al programa del equipo.

## Transporte y autenticación

Enviar HTTP POST con `Content-Type: application/json` mediante el transporte HTTP existente del gateway.
Usar HTTPS para el acceso externo cuando esté habilitado; no incluir tokens en las URLs.
Las rutas siguientes son relativas al mismo servidor del dashboard.
Los tiempos de medición y de trabajo son los del equipo, no la recepción del servidor.

| Uso | Ruta | Autenticación |
| --- | --- | --- |
| Actividad terminada | `/api/v1/lorawan/linea9-cycle` | `Authorization: Bearer <TOKEN_LORA_EXISTENTE>` o `X-Milesight-Token` existente |
| Temperatura exterior | `/api/v1/sensors/exterior` | `Authorization: Bearer <SENSOR_INGEST_TOKEN>` |
| Temperatura y CO₂ interior | `/api/v1/sensors/interior` | `Authorization: Bearer <SENSOR_INGEST_TOKEN>` |

La clave de sensores se configura en el servidor y se entrega al integrador por un canal privado.
No se incluye ninguna clave real en esta documentación. Las claves existentes de LoRa no cambian.
Los sensores deben estar en las listas autorizadas de su ubicación; enviar un ID inventado no autoriza un sensor.

## Actividades constructivas

Enviar UN mensaje `STAGE_END` al terminar cada intervalo de actividad con su inicio, fin y duración.
No es necesario un mensaje `STAGE_START` previo para este contrato.
`cycle_id` relaciona intervalos; no acredita por sí solo que un ciclo esté completo.
Un intervalo nuevo usa un `event_id` nuevo; una retransmisión usa el MISMO `event_id` y el mismo contenido de `object`.
Si una actividad se interrumpe y vuelve, son intervalos diferentes, incluso dentro del mismo ciclo.
Los IDs se distinguen por dispositivo. Se normaliza `devEUI` a mayúsculas y sin espacios exteriores.

```json
{
  "devEUI": "A8404180C45D1554",
  "object": {
    "event_id": "tunel-20261112-001",
    "event_type": "STAGE_END",
    "cycle_id": "ciclo-20261112-001",
    "stage_code": "shotcrete",
    "front": "Frente Norte",
    "shift": "Día",
    "inicio_evento": "2026-11-12T13:00:00-03:00",
    "fin_evento": "2026-11-12T14:00:00-03:00",
    "duration_seconds": 3600,
    "estado_sello": "sin_aplicar",
    "confidence": 0.92
  }
}
```

| Campo de object | Obligatorio | Regla |
| --- | --- | --- |
| event_id | Sí | String de 1 a 100 caracteres; estable al retransmitir |
| event_type | Sí | STAGE_END para el contrato nuevo |
| cycle_id | Sí | String de 1 a 100 caracteres |
| stage_code | Sí | excavation, topography, shotcrete o mesh_frames |
| inicio_evento | Sí | Fecha y hora ISO 8601 con desfase o Z |
| fin_evento | Sí | Fecha y hora ISO 8601 con desfase o Z; no anterior al inicio |
| duration_seconds | Sí | Entero >= 0; coincide con fin menos inicio, tolerancia de 1 segundo |
| estado_sello | Sí | sin_aplicar, aplicado o desconocido; estado AL INICIO del intervalo |
| front | No | Por defecto Frente Norte; enviarlo explícitamente en producción |
| shift | No | Por defecto Día; enviarlo explícitamente en producción |
| confidence | No | Entre 0 y 1; por defecto 0. Confianza de la actividad, no del segundo modelo |

No enviar directamente `hp1` ni `partial_seal` en el contrato nuevo: el backend los calcula.
`stage_name` y `sequence` no son necesarios. El nombre final lo determina el backend.
Para otras actividades, usar `estado_sello: "desconocido"` si no existe una observación válida del sello.
No sustituir desconocido por sin_aplicar. No reutilizar un estado de otro frente.
El emisor debe congelar la observación del sello al inicio; el backend no puede comprobar visualmente si esa observación era correcta.
Usar el desfase que corresponda a la fecha; no fijar -03:00 todo el año.
La fecha completa permite intervalos que cruzan medianoche. El almacenamiento normalizado usa UTC.

| stage_code recibido | estado_sello | stage_code guardado | Estado |
| --- | --- | --- | --- |
| shotcrete | sin_aplicar | partial_seal (Sello) | CLASSIFIED |
| shotcrete | aplicado | hp1 (HP1) | CLASSIFIED |
| shotcrete | desconocido | shotcrete | PENDING |
| excavation, topography, mesh_frames | Cualquiera válido | Sin cambio | CLASSIFIED |

Ejemplo de respuesta inicial:
```json
{
  "status": "success",
  "duplicate": false,
  "event_id": "tunel-20261112-001",
  "cycle_id": "ciclo-20261112-001",
  "event_type": "STAGE_END",
  "detected_stage_code": "shotcrete",
  "stage_code": "partial_seal",
  "stage_name": "Sello",
  "classification_status": "CLASSIFIED",
  "received_at": "2026-11-12T17:00:00Z"
}
```
`received_at` es ilustrativo: será la hora real en que el servidor guardó el mensaje.
Cambios de fCnt, RSSI o SNR en una retransmisión no duplican la actividad.
Cambiar el contenido validado de `object` con el mismo ID produce 409; no reemplaza registros ya guardados.
No hay endpoint de corrección manual en esta entrega; los pendientes permanecen identificables para revisión posterior.

## Sensor exterior

```json
{
  "event_id": "exterior-20261112-001",
  "device_id": "SENSOR-EXT-001",
  "measured_at": "2026-11-12T13:00:00-03:00",
  "temperature_c": 12.5
}
```

## Sensor interior

```json
{
  "event_id": "interior-20261112-001",
  "device_id": "SENSOR-INT-001",
  "measured_at": "2026-11-12T13:00:00-03:00",
  "temperature_c": 18.2,
  "co2_ppm": 850
}
```

Todos los campos del ejemplo de cada sensor son obligatorios. `device_id` y `event_id`: strings de 1 a 100 caracteres.
`measured_at` requiere zona horaria. Temperatura en °C (-80 a 100), CO₂ en ppm (0 a 1.000.000), números finitos.
Estos son límites de validación técnica, no umbrales de salud ni de alarma.
No se aceptan campos extra en los mensajes de sensores; no enviar CO₂ al endpoint exterior.
Los IDs mostrados son una asignación propuesta; pueden usarse tal cual si el integrador los configura así y se autorizan en AWS.
La frecuencia de envío la acuerda la operación; el backend no la fija.

## Respuestas y reintentos

| HTTP | Significado | Acción del emisor |
| --- | --- | --- |
| 201 | Registro nuevo guardado | Retirar de la cola |
| 200 y duplicate=true | Retransmisión de un registro existente | Retirar de la cola |
| 401 | Credencial ausente o incorrecta | Corregir autenticación |
| 403 | Dispositivo no autorizado para este endpoint | Coordinar ID y ubicación |
| 409 | Mismo event_id con contenido distinto | Revisar el emisor; no crear otro ID automáticamente para el mismo trabajo |
| 422 | Estructura, fechas o valores inválidos | Corregir mensaje |
| 503 en sensores | Falta configurar token de sensores | Completar configuración del servidor |
| Fallo de red o 5xx | Confirmación no disponible | Conservar mensaje; reintentar con mismo ID y espera creciente |

## Consultas disponibles

- GET `/api/v1/sensors/readings?location=interior&limit=100`, con token de sensores. Filtro opcional `device_id`; límite de 1 a 1000; orden por hora de medición descendente.
- GET `/api/v1/lorawan/linea9-construction-events?cycle_id=ciclo-20261112-001&limit=100`, con token LoRa existente. Filtro opcional `device_id`; límite de 1 a 1000; orden por inicio descendente.
- Los endpoints actuales de estado, actividades y el historial conservan sus rutas. El historial y Excel incorporan inicio, fin, sello, actividad detectada y clasificación.
- El filtrado del historial antiguo sigue usando la fecha de recepción existente. Una llegada tardía no cambia automáticamente de día ese historial. Para trabajo, consultar inicio/fin de los registros nuevos.

## Persistencia y compatibilidad

Se agregan `sensor_readings` y `construction_activities` y se conserva `raw_events` como registro de recepción.
En actividades nuevas, `received_object` conserva el objeto validado recibido y `object` contiene la clasificación usada por las consultas actuales.
El guardado del evento crudo y del registro normalizado es una sola transacción. Una restricción única en la identidad de recepción evita registros repetidos.
No se borran históricos, no se reinterpretan mensajes antiguos, no se modifican pesos de modelos.
Los mensajes antiguos sin los campos nuevos conservan su comportamiento. No tienen la garantía nueva de idempotencia si no traen ID.
La ruta antigua de STAGE_START/STAGE_END guarda raw_events y no actualiza cycle_stages; esta entrega no reactiva esa lógica inalcanzable.
Las nuevas actividades se consultan desde construction_activities y el historial. No crean ciclos completos ni modifican los contadores de excavación automáticamente.
La visualización nueva de sensores, ciclo completo y revisión de pendientes se define en la siguiente etapa.
