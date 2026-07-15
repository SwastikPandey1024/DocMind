from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get(self, object_id: Any) -> ModelType | None:
        return self.db.get(self.model, object_id)

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        return list(self.db.scalars(statement).all())

    def create(self, *, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, db_obj: ModelType) -> None:
        if hasattr(db_obj, "is_deleted"):
            setattr(db_obj, "is_deleted", True)
            self.db.add(db_obj)
        else:
            self.db.delete(db_obj)
        self.db.commit()
