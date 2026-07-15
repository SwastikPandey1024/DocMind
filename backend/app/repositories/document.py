from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session) -> None:
        super().__init__(Document, db)

    def get_by_user_and_id(self, *, user_id, document_id):
        statement = (
            select(Document)
            .where(
                Document.user_id == user_id,
                Document.document_id == document_id,
                Document.is_deleted.is_(False),
            )
            .limit(1)
        )
        return self.db.scalar(statement)

    def list_by_user(self, *, user_id, offset: int = 0, limit: int = 100) -> list[Document]:
        statement = (
            select(Document)
            .where(Document.user_id == user_id, Document.is_deleted.is_(False))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_by_user_and_checksum(self, *, user_id, checksum: str) -> Document | None:
        statement = (
            select(Document)
            .where(
                Document.user_id == user_id,
                Document.checksum_sha256 == checksum,
                Document.is_deleted.is_(False),
            )
            .limit(1)
        )
        return self.db.scalar(statement)

