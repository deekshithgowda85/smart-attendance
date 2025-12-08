from fastapi import APIRouter, HTTPException
from ...schemas.auth import RegisterRequest, UserResponse
from ...core.security import hash_password
from ...db.mongo import db


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(payload: RegisterRequest):
    
    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long. Please use atmost 72 characters"
        )
    
    # Check existing user
    existing = await db.users.find_one({"email": payload.email})
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": payload.role,
    }
    
    # Add role specific data
    
    if payload.role == "student" :
        user_doc["branch"] = payload.branch
    elif payload.role == "teacher" :
        user_doc["employee_id"] = payload.employee_id
        user_doc["phone"] = payload.phone
        
    result = await db.users.insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "email": payload.email,
        "role": payload.role,
        "name": payload.name,
    }
        

# @router.post("/login", response_model=UserResponse)
# async def login(payload: LoginRequest):
#     email = payload.email
#     password = payload.password

#     fake_users = get_fake_users()
#     user = fake_users.get(email)

#     if not user or user["password"] != password:
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     return UserResponse(
#         email=email,
#         role=user["role"],
#         name=user["name"],
#     )
