from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    email: str
    role: str
    name: str

class RegisterRequest(BaseModel):
    role: str
    name: str
    email: EmailStr
    password: constr(min_length=6, max_length=72)
    
    # Student
    branch: Optional[str] = None
    
    # Teacher 
    employee_id: Optional[str] = None
    phone: Optional[str] = None