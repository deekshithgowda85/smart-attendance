from fastapi import APIRouter
from typing import List
from ...schemas.user import Student
from ...db.mongo import db

router = APIRouter(prefix="/api", tags=["Students"])

# --- in-memory stub DB (from your old main.py) ---
STUDENTS = [
    {"roll": "2101", "name": "Ravi Kumar", "attendance": 72},
    {"roll": "2045", "name": "Asha Patel", "attendance": 71},
    {"roll": "2122", "name": "Mira Singh", "attendance": 95},
]


@router.get("/students", response_model=List[Student])
async def get_students():
    return STUDENTS


@router.get("/test")
async def test_mongo():
    collections = await db.list_collection_names()
    return {"collections ": collections}
