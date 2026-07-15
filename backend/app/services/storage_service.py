from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.settings import get_settings


class StorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def build_document_dir(self, *, user_id: uuid.UUID, document_id: uuid.UUID) -> Path:
        # Deterministic directory structure.
        return self.upload_dir / str(user_id) / str(document_id)

    def sha256_fileobj(self, fileobj: BinaryIO) -> str:
        hasher = hashlib.sha256()
        for chunk in iter(lambda: fileobj.read(1024 * 1024), b""):
            hasher.update(chunk)
        return hasher.hexdigest()

    def save_upload(
        self,
        *,
        fileobj: BinaryIO,
        user_id: uuid.UUID,
        document_id: uuid.UUID,
        original_filename: str,
        mime_type: str,
    ) -> tuple[Path, str]:
        document_dir = self.build_document_dir(user_id=user_id, document_id=document_id)
        document_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(original_filename).suffix
        stored_filename = f"{document_id}{extension}" if extension else f"{document_id}"
        dest_path = document_dir / stored_filename

        # Hash and reset pointer should be handled by caller when needed.
        with open(dest_path, "wb") as out:
            for chunk in iter(lambda: fileobj.read(1024 * 1024), b""):
                out.write(chunk)

        return dest_path, mime_type

