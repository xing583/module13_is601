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
# ============================================================
# Final Project: User Profile & Password Change Schemas
# ============================================================

class UserUpdate(BaseModel):
    """
    Schema for updating user profile (username and/or email).
    Both fields are optional — user can update one or both.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.strip()

    @model_validator(mode="after")
    def at_least_one_field(self):
        """Reject empty update requests — must provide at least one field."""
        if self.username is None and self.email is None:
            raise ValueError("At least one field (username or email) must be provided")
        return self


class PasswordChange(BaseModel):
    """
    Schema for changing user password.
    Requires old password (for verification) + new password (twice).
    """
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Enforce stronger password rules than registration:
          - At least 8 characters
          - At least 1 uppercase letter
          - At least 1 lowercase letter
          - At least 1 digit
        """
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("New password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("New password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("New password must contain at least one digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        """Ensure new_password and confirm_password match."""
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirmation do not match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from the old password")
        return self


class UserProfile(BaseModel):
    """
    Schema for returning user profile with extra stats (Innovation feature).
    Includes total calculations count for personalization.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    total_calculations: int = 0

    model_config = {"from_attributes": True}
