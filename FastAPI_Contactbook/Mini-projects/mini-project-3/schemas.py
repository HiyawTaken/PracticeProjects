from pydantic import BaseModel

# Base schema (fields shared by creating and reading)
class UserBase(BaseModel):
    email: str

# Schema for CREATING a user (passwords are only needed here)
class UserCreate(UserBase):
    password: str

# Schema for READING a user (we return ID and status, but NEVER password)
class UserResponse(UserBase):
    id: int
    is_active: bool

    # Config to tell Pydantic to read data from the ORM model
    class Config:
        from_attributes = True