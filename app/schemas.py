from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.calculator import CalculationType

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    username: str
    password: str

class CalculationUpdate(BaseModel):
    a: Optional[float] = None
    b: Optional[float] = None
    type: Optional[CalculationType] = None
    user_id: Optional[int] = None

    @model_validator(mode="after")
    def check_divide_by_zero(self):
        if self.type == CalculationType.DIVIDE and self.b is not None and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self

class CalculationCreate(BaseModel):
    a: float
    b: float
    type: CalculationType
    user_id: Optional[int] = None

    @model_validator(mode="after")
    def check_divide_by_zero(self):
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self

class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: str
    result: float
    created_at: datetime
    user_id: Optional[int] = None

    model_config = {"from_attributes": True}
