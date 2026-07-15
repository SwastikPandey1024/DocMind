from pydantic import BaseModel, EmailStr


class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
