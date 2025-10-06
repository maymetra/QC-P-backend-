# app/api/v1/files.py
import uuid
import os
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from app.api import deps
from app.db import models

router = APIRouter(prefix="/files", tags=["Files"])

# Определяем базовую директорию для медиафайлов
MEDIA_ROOT = Path("media")


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
    # Создаем структурированный путь: media/project_12/item_150/
    upload_dir = MEDIA_ROOT / f"project_{project_id}" / f"item_{item_id}"
    os.makedirs(upload_dir, exist_ok=True)

    # Генерируем уникальное имя файла, чтобы избежать конфликтов
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Сохраняем файл на диск
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save file.")

    # Возвращаем метаданные, которые фронтенд сохранит в Item
    return {
        "uid": str(uuid.uuid4()),  # Генерируем uid для Ant Design
        "name": file.filename,
        "file_path": str(file_path).replace("\\", "/"),  # Возвращаем путь в POSIX-формате
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
    # Формируем путь к файлу
    file_path = MEDIA_ROOT / f"project_{project_id}" / f"item_{item_id}" / filename

    # Проверка безопасности: существует ли файл и имеет ли пользователь доступ к проекту
    # (Здесь должна быть ваша логика проверки прав доступа к project_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(path=file_path, filename=filename)