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
