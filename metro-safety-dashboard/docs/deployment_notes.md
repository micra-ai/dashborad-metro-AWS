# Notas de Despliegue en AWS

El proyecto está diseñado para poder escalar de forma sencilla al ecosistema de AWS.

## Componentes Sugeridos
1. **Base de Datos:** AWS RDS con motor PostgreSQL. 
   - Modifique la variable `DATABASE_URL` en su entorno de producción para que apunte a la instancia RDS (ej. `postgresql://user:password@rds-host:5432/dbname`). 
   - SQLAlchemy abstraerá la conexión de manera automática.

2. **Backend (API FastAPI):** 
   - **Opción 1 (Recomendada):** AWS App Runner o AWS ECS (Elastic Container Service) utilizando el `docker-compose.yml` o construyendo un `Dockerfile` a partir del directorio backend.
   - **Opción 2:** Despliegue tradicional en EC2, configurando Nginx como reverse proxy hacia Gunicorn/Uvicorn.

3. **Frontend (HTML/JS/CSS):** 
   - Al ser archivos estáticos puros ("Vanilla JS"), lo más eficiente es subirlos a un bucket de **AWS S3** configurado como "Static Website Hosting".
   - Utilice **AWS CloudFront** en frente del S3 para proveer CDN, SSL/HTTPS y baja latencia.

## Consideraciones Críticas de Seguridad
- Cambie **obligatoriamente** el `SECRET_KEY` en el entorno de AWS por una clave fuerte.
- Ajuste el `CORS_ORIGINS` para que únicamente la URL de su CloudFront/S3 esté permitida.
- Configure el Security Group de su base de datos RDS para que solo acepte conexiones desde las instancias/servicios del Backend.
