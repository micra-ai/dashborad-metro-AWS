# Notas de Integración

Este proyecto desacopla la lógica de integración de los dispositivos (que son externos) de la lógica de negocio y presentación del dashboard.

## ¿Qué hacer si cambian los JSON de los dispositivos?

1. **Variables Simples:** Si cambian IDs de dispositivos, umbrales aceptables o mapeos simples, dirígete a `backend/app/integration_config/` y edita los diccionarios o variables. No es necesario tocar los servicios de lógica de negocio.
2. **Estructura JSON:** Si la estructura del JSON cambia drásticamente, debes actualizar los esquemas Pydantic correspondientes en `backend/app/schemas/`.
3. **Mapeo a la BD (El paso clave):** Si la base de datos se mantiene pero la estructura de entrada cambia, ajusta la lógica en `backend/app/normalizers/`. Los normalizadores actúan como una capa "anti-corrupción" asegurando que, independientemente del formato de entrada, los eventos lleguen a la base de datos y al dashboard de forma predecible y estandarizada.

### Regla de Oro
**Nunca conectar directamente el frontend al JSON crudo enviado por los dispositivos.** Siempre debe pasar por la validación de Pydantic, la normalización interna, y guardarse como un modelo interno estable antes de servirse a través de `/api/dashboard/*`.
