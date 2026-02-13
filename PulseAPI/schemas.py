from pydantic import BaseModel
from datetime import datetime

class TargetBase(BaseModel):
    name: str
    url: str

class TargetResponse(TargetBase):
    id: int
    status_code: int
    last_checked: datetime

    class Config:
        from_attributes = True
