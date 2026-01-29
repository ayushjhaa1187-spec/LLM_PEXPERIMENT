"""Pydantic schemas for Phase 1"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator

# USER SCHEMAS
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(default='viewer')

class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# DOCUMENT SCHEMAS
class DocumentBase(BaseModel):
    filename: str = Field(..., max_length=255)
    file_type: str = Field(..., max_length=10)
    size: int = Field(..., gt=0)

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# QUERY SCHEMAS
class QueryCreate(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    context: Optional[List[int]] = None

class QueryResponse(BaseModel):
    id: int
    user_id: int
    question: str
    answer: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ERROR SCHEMAS
class ErrorResponse(BaseModel):
    error: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None

# TOKEN SCHEMAS
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_in: int

# HEALTH CHECK
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
