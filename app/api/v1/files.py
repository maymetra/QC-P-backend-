# app/api/v1/files.py
import uuid
import os
from pathlib import Path
import re
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from app.api import deps
from app.db import models

router = APIRouter(prefix="/files", tags=["Files"])

MEDIA_ROOT = Path("media")

def secure_filename(filename: str) -> str:
    """
    Санитизирует имя файла, удаляя недопустимые символы.
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '', filename)


@router.post("/upload/{project_id}/{item_id}")
async def upload_file(
        project_id: int,
        item_id: int,
        file: UploadFile = File(...),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    Загружает файл на сервер.
    """
    upload_dir = MEDIA_ROOT / f"project_{project_id}" / f"item_{item_id}"
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save file.")

    return {
        "uid": str(uuid.uuid4()),
        "name": file.filename,
        "file_path": unique_filename,
    }


@router.get("/{project_id}/{item_id}/{filename}")
def download_file(
        project_id: int,
        item_id: int,
        filename: str,
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    Безопасно отдает файл для скачивания.
    """
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    file_path = MEDIA_ROOT / f"project_{project_id}" / f"item_{item_id}" / safe_filename

    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(path=file_path, filename=safe_filename)