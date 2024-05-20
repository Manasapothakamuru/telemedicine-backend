from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.health_data_model import HealthData
import bcrypt
from typing import Optional
from datetime import datetime, date
import logging

app = FastAPI()

# Initialize MongoDB Client
db_client = AsyncIOMotorClient('mongodb://localhost:27017')
db = db_client.mydatabase

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class Credentials(BaseModel):
    username: str
    password: str

class User(BaseModel):
    user_id: Optional[str] = None  # Explicitly setting default to None
    name: str
    role: str
    state: str
    dob: datetime
    credentials: Credentials

class HealthData(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    date: date
    weight: float

@app.post("/users/", response_model=User)
async def create_user(user: User):
    user_dict = user.dict(by_alias=True, exclude_unset=True)
    user_dict['credentials']['password'] = hash_password(user_dict['credentials']['password'])
    try:
        result = await db.users.insert_one(user_dict)
        user_dict['user_id'] = str(result.inserted_id)  # Ensure the _id is captured correctly
        return user_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error inserting user: {str(e)}")

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    try:
        user_data = await db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data['user_id'] = str(user_data['_id'])  # Ensure proper conversion of _id to string
            return user_data
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

# Assuming HealthData model and its related routes are correctly defined and don't need changes for this issue.


@app.post("/health_data/", response_model=HealthData)
async def create_health_data(health_data: HealthData):
    health_data_dict = health_data.dict(by_alias=True, exclude_unset=True)
    try:
        # Convert 'date' field from date to datetime
        health_data_dict['date'] = datetime.combine(health_data_dict['date'], datetime.min.time())
        health_data_dict.pop('id', None)  # Ensure no null id is sent
        logging.info(f"Health data to insert: {health_data_dict}")  # Log the health data being inserted
        result = await db.health_data.insert_one(health_data_dict)
        health_data_dict['_id'] = str(result.inserted_id)  # Convert ObjectId to string
        return health_data_dict
    except Exception as e:
        logging.error(f"Error inserting health data: {e}")
        raise HTTPException(status_code=400, detail=f"Error inserting health data: {str(e)}")


@app.get("/health_data/{user_id}", response_model=list[HealthData])
async def get_health_data(user_id: str):
    try:
        health_data_list = await db.health_data.find({"user_id": user_id}).to_list(100)
        # Convert ObjectId to string for each health data record
        for health_data in health_data_list:
            if '_id' in health_data:
                health_data['_id'] = str(health_data['_id'])
        return health_data_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving health data: {str(e)}")