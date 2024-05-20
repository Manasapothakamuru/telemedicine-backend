# health_data_model.py
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional

class HealthData(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str  # Reference to the User collection
    date: date
    weight: float

    @validator('weight')
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError("Weight must be a positive number")
        return v
    @validator('date', pre=True, always=True)
    def convert_date(cls, v):
        return datetime.combine(v, datetime.min.time()) if isinstance(v, date) else v
    @validator('id', pre=True, always=True)
    def convert_id(cls, v):
        return str(v) if isinstance(v, ObjectId) else v
