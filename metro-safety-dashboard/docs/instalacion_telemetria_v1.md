# Instalación en AWS — telemetría Línea 9

Esta actualización parte de la versión sincronizada desde AWS, commit 902fffa.
Se entrega en una rama de implementación; instalar después de revisar el cambio.
No se ha conectado al servidor ni reiniciado el servicio desde este trabajo.

## Antes de cambiar archivos

1. Confirmar que el repositorio de AWS no tiene modificaciones pendientes con `git status --short`.
2. Respaldar el código, el `.env` real y la base de datos que utiliza el servicio. No subir estos respaldos a GitHub.
3. Para SQLite, usar una copia consistente mediante el comando `.backup` de sqlite3 o su API de backup; no copiar únicamente el archivo .db mientras hay escrituras.
4. Confirmar el intérprete, directorio de trabajo y nombre real del servicio; el servicio usado anteriormente es `metro-backend.service`.

## Preparar un checkout separado

Desde `/home/ubuntu/dashborad-metro-AWS`:

```bash
git fetch origin
git worktree add /home/ubuntu/metro-telemetria-prueba origin/feat/linea9-sensores-sello-hp1-20261113
```

Esto permite revisar sin reemplazar aún los archivos del servicio en ejecución.
Usar un entorno virtual de prueba y una base SQLite de prueba; no apuntar los tests a la base real.
Dentro del backend del checkout de prueba:

```bash
python3 -m venv /home/ubuntu/venv-metro-prueba
/home/ubuntu/venv-metro-prueba/bin/pip install -r requirements.txt httpx
DATABASE_URL=sqlite:////tmp/metro-telemetria-prueba.db /home/ubuntu/venv-metro-prueba/bin/python -m pytest -q
```

Probar el backend en un puerto local alternativo, por ejemplo 8001, sin detener el proceso de producción:

```bash
DATABASE_URL=sqlite:////tmp/metro-telemetria-prueba.db /home/ubuntu/venv-metro-prueba/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Para una prueba HTTP de sensores, configurar token e IDs solamente en el entorno de esa prueba.
No enviar datos ficticios al endpoint productivo: aparecerían en el historial.

## Configuración para sensores

En el `.env` REAL utilizado por el servicio, agregar estas variables una vez; no reemplazar todo el archivo:

```dotenv
SENSOR_INGEST_TOKEN=<GENERAR_UN_TOKEN_PRIVADO>
SENSOR_EXTERIOR_DEVICES=SENSOR-EXT-001
SENSOR_INTERIOR_DEVICES=SENSOR-INT-001
```

Generar el token localmente en AWS con `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`.
Sustituir el marcador por el valor generado y compartirlo solo con el integrador por un canal privado.
Los IDs pueden ser los de la propuesta o los reales acordados; listas separadas por coma.
Sin token, el endpoint de sensores responde 503. Sin ID autorizado, responde 403.
No es necesario cambiar el token LoRa existente. No subir el `.env` a GitHub.

## Aplicar después de la revisión

Una vez integrado el cambio en main y validado el respaldo:

```bash
cd /home/ubuntu/dashborad-metro-AWS
git status --short
git pull --ff-only origin main
```

Si hay cambios locales o diverge la rama, detenerse y revisarlos; no usar reset --hard ni force.
Usar el mismo entorno virtual existente de producción. No actualizar dependencias de producción indiscriminadamente.
No se agregan dependencias de runtime: se usan FastAPI, Pydantic 2 y SQLAlchemy ya utilizados.
`httpx` se necesita solo para ejecutar los tests HTTP.

Al importar `app.main`, `Base.metadata.create_all` crea las dos tablas nuevas en la base configurada.
No altera columnas de tablas existentes ni migra datos previos. El usuario de base debe tener permiso CREATE TABLE.

```bash
sudo systemctl restart metro-backend.service
sudo systemctl is-active metro-backend.service
curl --fail http://127.0.0.1:8000/api/health
```

Comprobar `/openapi.json`: deben figurar los endpoints de sensores y la consulta de actividades.
Hacer después una prueba desde el gateway con datos reales y revisar el registro guardado.
La configuración Nginx del repo ya reenvía `/api/` sin quitar el prefijo. Si la configuración REAL difiere, verificar estas rutas también a través del dominio antes de habilitar el envío.
La prueba local no certifica el proxy, los permisos ni las variables de AWS.

## Reversión

Respaldar el `.env` antes de editarlo. Si falla el arranque, revisar el log del servicio en AWS sin compartir credenciales.
Para volver al código anterior, usar el commit previo en un checkout o despliegue controlado y reiniciar el servicio con ese código.
No ejecutar un reset destructivo sobre cambios locales.
Las tablas nuevas pueden quedarse en la base: el código anterior no las consulta. No borrarlas ni restaurar una base vieja si ya llegaron nuevos eventos, porque se perderían registros posteriores al respaldo.

## Validación realizada

33 tests aprobados en una base SQLite de prueba: 28 de la actualización y 5 existentes.
Casos cubiertos: clasificación de los tres estados, otras actividades, fechas con desfase y cruce de medianoche, validación de duración, duplicados y conflicto, autenticación, dispositivos, sensores interior/exterior, consultas, historial y compatibilidad de mensajes antiguos.
Se comprobó además la importación de app.main, creación de tablas nuevas y generación de OpenAPI en una base de prueba.
Las advertencias observadas corresponden a APIs deprecadas del código existente y del entorno de tests; no hubo fallos de tests.
