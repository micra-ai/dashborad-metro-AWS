import os
import base64
import re
from fastapi import UploadFile

# The BASE_DIR should be the directory that contains the app and static folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

def ensure_images_dir():
    os.makedirs(IMAGES_DIR, exist_ok=True)

def save_base64_image(base64_str: str, event_id: str) -> str:
    """
    Decodifica una imagen en base64 y la guarda localmente en el directorio de imágenes estáticas.
    Retorna la URL relativa para acceder a ella.
    """
    ensure_images_dir()
    
    # Check if the string has a base64 header (e.g., data:image/jpeg;base64,...)
    header = ""
    if "," in base64_str:
        header, base64_str = base64_str.split(",", 1)
        
    # Check extension from header or default to jpg
    ext = "jpg"
    if "png" in header.lower():
        ext = "png"
    elif "gif" in header.lower():
        ext = "gif"
        
    image_data = base64.b64decode(base64_str)
    filename = f"{event_id}.{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_data)
        
    return f"/static/images/{filename}"

def save_uploaded_file(file: UploadFile, event_id: str) -> str:
    """
    Guarda un archivo de imagen subido directamente y retorna su URL relativa.
    """
    ensure_images_dir()
    
    # Safe extension lookup
    ext = "jpg"
    if file.filename:
        _, file_ext = os.path.splitext(file.filename)
        if file_ext:
            ext = file_ext.lstrip(".")
            
    filename = f"{event_id}.{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    
    # Reset file pointer to read from start
    file.file.seek(0)
    with open(filepath, "wb") as f:
        while content := file.file.read(1024 * 1024):
            f.write(content)
            
    return f"/static/images/{filename}"
