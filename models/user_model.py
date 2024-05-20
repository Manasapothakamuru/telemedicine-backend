from pydantic import BaseModel, Field, validator
from datetime import datetime  # Changed from date to datetime
from typing import Optional

class User(BaseModel):
    user_id: Optional[str] = Field(default=None, alias="_id")
    name: str
    role: str
    state: str
    dob: datetime  # Changed from date to datetime
    credentials: dict

    @validator('role')
    def validate_role(cls, v):
        if v not in ["customer", "provider"]:
            raise ValueError("Role must be either 'customer' or 'provider'")
        return v

    @validator('credentials', pre=True)
    def validate_credentials(cls, v):
        if 'username' not in v or 'password' not in v:
            raise ValueError("Credentials must contain username and password")
        return v
