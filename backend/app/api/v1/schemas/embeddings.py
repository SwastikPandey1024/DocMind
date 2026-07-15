from pydantic import BaseModel


class EmbeddingResponse(BaseModel):
    status: str
