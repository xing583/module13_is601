import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from jose import jwt, JWTError

from app.database import engine, get_db, Base
from app.models import User, Calculation
from app.schemas import (
    UserCreate, UserRead, UserLogin,
    CalculationCreate, CalculationRead, CalculationUpdate,
    UserUpdate, PasswordChange, UserProfile,  # Final Project: profile & password change
)
from app.calculator import CalculationFactory

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "my-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================
# Final Project: JWT Authentication Dependency
# ============================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode JWT and return the currently logged-in user.
    Raises 401 if token is missing, invalid, or user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user


Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Auth & Calculation API", version="3.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================
# Page routes (serve HTML files)
# ============================================================

@app.get("/")
def home():
    return FileResponse("static/login.html")

@app.get("/login")
def login_page():
    return FileResponse("static/login.html")

@app.get("/register")
def register_page():
    return FileResponse("static/register.html")

@app.get("/calculations-page")
def calculations_page():
    """Serve the calculations BREAD page."""
    return FileResponse("static/calculations.html")

@app.get("/profile")
def profile_page():
    """Final Project: Serve the user profile & password change page."""
    return FileResponse("static/profile.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}


# ============================================================
# Auth routes: register & login
# ============================================================

@app.post("/users/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed = User.hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    token = create_access_token({"sub": db_user.username, "user_id": db_user.id})
    return {
        "message": "Registration successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username,
    }

@app.post("/users/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not User.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }


# ============================================================
# Final Project: User Profile & Password Change Endpoints
# IMPORTANT: These specific routes MUST be defined BEFORE
# /users/{user_id} so FastAPI doesn't treat "me" as an integer.
# ============================================================

@app.get("/users/me", response_model=UserProfile)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the current user's profile, including total calculation count.
    The calculation count is an Innovation feature for personalized stats.
    """
    total = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).count()
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        total_calculations=total,
    )


@app.put("/users/me", response_model=UserProfile)
def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the current user's username and/or email.
    Returns 409 if the new username/email conflicts with another user.
    """
    if data.username is not None:
        current_user.username = data.username
    if data.email is not None:
        current_user.email = data.email

    try:
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken by another user",
        )

    total = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).count()
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        total_calculations=total,
    )


@app.post("/users/me/password", status_code=status.HTTP_200_OK)
def change_my_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change the current user's password.
    Requires the old password for verification (defense against session hijacking).
    """
    # Step 1: verify old password
    if not User.verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
        )

    # Step 2: hash and save the new password
    current_user.password_hash = User.hash_password(data.new_password)
    db.commit()

    return {
        "message": "Password changed successfully. Please log in again with your new password."
    }


# ============================================================
# User routes with path parameters (must come AFTER /users/me)
# ============================================================

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================
# Calculation BREAD routes
# ============================================================

@app.get("/calculations", response_model=List[CalculationRead])
def browse_calculations(user_id: int = None, db: Session = Depends(get_db)):
    if user_id:
        return db.query(Calculation).filter(Calculation.user_id == user_id).all()
    return db.query(Calculation).all()

@app.get("/calculations/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.get(Calculation, calc_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc

@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(data: CalculationCreate, db: Session = Depends(get_db)):
    operation = CalculationFactory.create(data.type)
    result = operation.calculate(data.a, data.b)
    calc = Calculation(
        a=data.a, b=data.b,
        type=data.type.value, result=result,
        user_id=data.user_id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc

@app.put("/calculations/{calc_id}", response_model=CalculationRead)
def edit_calculation(calc_id: int, data: CalculationUpdate, db: Session = Depends(get_db)):
    calc = db.get(Calculation, calc_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if data.a is not None:
        calc.a = data.a
    if data.b is not None:
        calc.b = data.b
    if data.type is not None:
        calc.type = data.type.value
    if data.user_id is not None:
        calc.user_id = data.user_id
    from app.calculator import CalculationType as CT
    operation = CalculationFactory.create(CT(calc.type))
    calc.result = operation.calculate(calc.a, calc.b)
    db.commit()
    db.refresh(calc)
    return calc

@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.get(Calculation, calc_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calc)
    db.commit()
    return None
