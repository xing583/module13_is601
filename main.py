import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from jose import jwt

from app.database import engine, get_db, Base
from app.models import User, Calculation
from app.schemas import (
    UserCreate, UserRead, UserLogin,
    CalculationCreate, CalculationRead, CalculationUpdate,
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

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Auth & Calculation API", version="3.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/login.html")

@app.get("/login")
def login_page():
    return FileResponse("static/login.html")

@app.get("/register")
def register_page():
    return FileResponse("static/register.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}

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

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/calculations", response_model=List[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
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
