import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://user:password@db:5432/appdb"
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


# ============================================================
# Final Project: Integration tests for profile & password endpoints
# ============================================================

def _register_and_login(username="profileuser", email="profile@test.com", password="OldPass123"):
    """Helper: 注册用户 + 返回 token, 测试要用就调它."""
    client.post("/users/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    resp = client.post("/users/login", json={
        "username": username,
        "password": password,
    })
    return resp.json()["access_token"]


# -------------------- GET /users/me --------------------

def test_get_me_unauthorized_no_token():
    """未带 token 访问应该返回 401"""
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_get_me_unauthorized_invalid_token():
    """带错误的 token 应该返回 401"""
    resp = client.get("/users/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_get_me_returns_profile_with_token():
    """带正确 token 应该返回 200 + profile 数据"""
    token = _register_and_login(username="getmeuser", email="getme@test.com")
    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "getmeuser"
    assert data["email"] == "getme@test.com"


def test_get_me_includes_total_calculations():
    """profile 应该包含 total_calculations 字段 (Innovation feature)"""
    token = _register_and_login(username="calcuser", email="calc@test.com")
    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    data = resp.json()
    assert "total_calculations" in data
    assert data["total_calculations"] == 0


# -------------------- PUT /users/me --------------------

def test_put_me_update_email():
    """改 email 成功后, 再 GET 应该看到新 email"""
    token = _register_and_login(username="updemail", email="old@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put("/users/me", headers=headers, json={"email": "new@test.com"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@test.com"

    resp2 = client.get("/users/me", headers=headers)
    assert resp2.json()["email"] == "new@test.com"


def test_put_me_update_username():
    """改 username 成功"""
    token = _register_and_login(username="oldname", email="username@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put("/users/me", headers=headers, json={"username": "newname"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "newname"


def test_put_me_unauthorized():
    """未登录改 profile 应该返回 401"""
    resp = client.put("/users/me", json={"email": "hacker@test.com"})
    assert resp.status_code == 401


def test_put_me_username_conflict():
    """用别人已经占用的 username 应该返回 409"""
    client.post("/users/register", json={
        "username": "userA",
        "email": "a@test.com",
        "password": "PassA123",
    })
    token = _register_and_login(username="userB", email="b@test.com")

    resp = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "userA"},
    )
    assert resp.status_code == 409


# -------------------- POST /users/me/password --------------------

def test_change_password_success():
    """改密码后, 旧密码应该失效, 新密码能登录"""
    token = _register_and_login(username="pwduser", email="pwd@test.com", password="OldPass123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/users/me/password", headers=headers, json={
        "old_password": "OldPass123",
        "new_password": "NewPass456",
        "confirm_password": "NewPass456",
    })
    assert resp.status_code == 200
    assert "successfully" in resp.json()["message"].lower()

    old_login = client.post("/users/login", json={
        "username": "pwduser",
        "password": "OldPass123",
    })
    assert old_login.status_code == 401

    new_login = client.post("/users/login", json={
        "username": "pwduser",
        "password": "NewPass456",
    })
    assert new_login.status_code == 200


def test_change_password_wrong_old():
    """旧密码错误应该返回 401"""
    token = _register_and_login(username="wrongolduser", email="wrong@test.com", password="OldPass123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/users/me/password", headers=headers, json={
        "old_password": "WrongOldPass",
        "new_password": "NewPass456",
        "confirm_password": "NewPass456",
    })
    assert resp.status_code == 401


def test_change_password_weak_new():
    """新密码太弱 (没有数字) 应该被 Pydantic 拒绝 (422)"""
    token = _register_and_login(username="weakuser", email="weak@test.com", password="OldPass123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/users/me/password", headers=headers, json={
        "old_password": "OldPass123",
        "new_password": "NoDigitHere",
        "confirm_password": "NoDigitHere",
    })
    assert resp.status_code == 422


def test_change_password_mismatch():
    """new_password 和 confirm_password 不匹配应该 422"""
    token = _register_and_login(username="matchuser", email="match@test.com", password="OldPass123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/users/me/password", headers=headers, json={
        "old_password": "OldPass123",
        "new_password": "NewPass456",
        "confirm_password": "DifferentOne",
    })
    assert resp.status_code == 422


def test_change_password_unauthorized():
    """未登录改密码应该返回 401"""
    resp = client.post("/users/me/password", json={
        "old_password": "X",
        "new_password": "Y",
        "confirm_password": "Y",
    })
    assert resp.status_code == 401
