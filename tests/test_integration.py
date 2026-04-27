import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://user:password@localhost:5432/appdb"
)

engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_user():
    resp = client.post("/users/register", json={
        "username": "integuser",
        "email": "integ@test.com",
        "password": "securepass123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"] == "Registration successful"
    assert "access_token" in data

def test_register_duplicate():
    client.post("/users/register", json={
        "username": "dupuser",
        "email": "dup@test.com",
        "password": "securepass123",
    })
    resp = client.post("/users/register", json={
        "username": "dupuser",
        "email": "dup@test.com",
        "password": "securepass123",
    })
    assert resp.status_code == 409

def test_login_success():
    client.post("/users/register", json={
        "username": "loginuser",
        "email": "login@test.com",
        "password": "securepass123",
    })
    resp = client.post("/users/login", json={
        "username": "loginuser",
        "password": "securepass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Login successful"
    assert "access_token" in data

def test_login_wrong_password():
    client.post("/users/register", json={
        "username": "wrongpw",
        "email": "wrong@test.com",
        "password": "securepass123",
    })
    resp = client.post("/users/login", json={
        "username": "wrongpw",
        "password": "badpassword",
    })
    assert resp.status_code == 401

def test_add_calculation():
    resp = client.post("/calculations", json={
        "a": 10, "b": 5, "type": "add",
    })
    assert resp.status_code == 201
    assert resp.json()["result"] == 15

def test_browse_calculations():
    client.post("/calculations", json={"a": 1, "b": 2, "type": "add"})
    resp = client.get("/calculations")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

def test_read_calculation():
    create = client.post("/calculations", json={"a": 8, "b": 4, "type": "subtract"})
    calc_id = create.json()["id"]
    resp = client.get(f"/calculations/{calc_id}")
    assert resp.status_code == 200
    assert resp.json()["result"] == 4

def test_edit_calculation():
    create = client.post("/calculations", json={"a": 2, "b": 3, "type": "multiply"})
    calc_id = create.json()["id"]
    resp = client.put(f"/calculations/{calc_id}", json={"a": 10})
    assert resp.status_code == 200
    assert resp.json()["result"] == 30

def test_delete_calculation():
    create = client.post("/calculations", json={"a": 9, "b": 3, "type": "divide"})
    calc_id = create.json()["id"]
    resp = client.delete(f"/calculations/{calc_id}")
    assert resp.status_code == 204
    resp2 = client.get(f"/calculations/{calc_id}")
    assert resp2.status_code == 404
