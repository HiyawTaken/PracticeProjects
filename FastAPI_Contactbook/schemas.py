from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    phone: str
    email: str | None = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


