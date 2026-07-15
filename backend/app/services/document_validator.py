from __future__ import annotations

import mimetypes
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    mime_type: str
    size_bytes: int


class DocumentValidator:
    def __init__(self, *, max_file_size_bytes: int = 20 * 1024 * 1024) -> None:
        self.max_file_size_bytes = max_file_size_bytes

    def validate_pdf(self, *, filename: str, content_type: str | None, size_bytes: int) -> ValidationResult:
        if size_bytes <= 0:
            raise ValueError("Uploaded file is empty.")

        if size_bytes > self.max_file_size_bytes:
            raise ValueError(f"File too large. Max size is {self.max_file_size_bytes} bytes.")

        # MIME validation.
        resolved_mime = (content_type or "").lower().strip()
        if not resolved_mime:
            # Best-effort fallback using filename.
            resolved_mime = mimetypes.guess_type(filename)[0] or ""

        allowed = {"application/pdf", "application/x-pdf", "application/acrobat"}
        if resolved_mime not in allowed:
            raise ValueError("Only PDF files are allowed.")

        return ValidationResult(mime_type=resolved_mime, size_bytes=size_bytes)

