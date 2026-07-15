from pydantic import BaseModel


class OCRProcessResponse(BaseModel):
    status: str
    pages: int


class OCRStatusResponse(BaseModel):
    status: str
