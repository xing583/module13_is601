import pytest
from app.models import User
from app.schemas import UserCreate, CalculationCreate
from app.calculator import CalculationFactory, CalculationType

def test_hash_password_returns_string():
    hashed = User.hash_password("testpassword")
    assert isinstance(hashed, str)
    assert hashed != "testpassword"

def test_verify_password_correct():
    hashed = User.hash_password("mypassword")
    assert User.verify_password("mypassword", hashed) is True

def test_verify_password_incorrect():
    hashed = User.hash_password("mypassword")
    assert User.verify_password("wrongpassword", hashed) is False

def test_user_create_valid():
    user = UserCreate(username="alice", email="alice@example.com", password="securepass")
    assert user.username == "alice"

def test_user_create_short_username():
    with pytest.raises(Exception):
        UserCreate(username="ab", email="a@b.com", password="securepass")

def test_user_create_short_password():
    with pytest.raises(Exception):
        UserCreate(username="alice", email="a@b.com", password="short")

def test_calculation_create_valid():
    calc = CalculationCreate(a=10, b=5, type=CalculationType.ADD)
    assert calc.a == 10

def test_calculation_divide_by_zero():
    with pytest.raises(Exception):
        CalculationCreate(a=10, b=0, type=CalculationType.DIVIDE)

def test_add():
    op = CalculationFactory.create(CalculationType.ADD)
    assert op.calculate(3, 4) == 7

def test_subtract():
    op = CalculationFactory.create(CalculationType.SUBTRACT)
    assert op.calculate(10, 3) == 7

def test_multiply():
    op = CalculationFactory.create(CalculationType.MULTIPLY)
    assert op.calculate(4, 5) == 20

def test_divide():
    op = CalculationFactory.create(CalculationType.DIVIDE)
    assert op.calculate(10, 2) == 5

def test_divide_by_zero_runtime():
    op = CalculationFactory.create(CalculationType.DIVIDE)
    with pytest.raises(ValueError):
        op.calculate(10, 0)

# ============================================================
# Final Project: Unit tests for new schemas
# UserUpdate, PasswordChange, UserProfile
# ============================================================
from app.schemas import UserUpdate, PasswordChange, UserProfile


# -------------------- UserUpdate schema --------------------

def test_user_update_username_only():
    """用户可以只更新 username, email 可以留空"""
    data = UserUpdate(username="newname")
    assert data.username == "newname"
    assert data.email is None


def test_user_update_email_only():
    """用户可以只更新 email, username 可以留空"""
    data = UserUpdate(email="newemail@test.com")
    assert data.email == "newemail@test.com"
    assert data.username is None


def test_user_update_empty_request_rejected():
    """两个字段都不传应该报错 (防止空请求浪费 DB 连接)"""
    with pytest.raises(Exception):
        UserUpdate()


def test_user_update_username_too_short():
    """username 少于 3 字符应该报错"""
    with pytest.raises(Exception):
        UserUpdate(username="ab")


# -------------------- PasswordChange schema --------------------

def test_password_change_valid():
    """合法的密码修改: 大小写 + 数字, 长度足够, 二次确认匹配"""
    data = PasswordChange(
        old_password="OldPass123",
        new_password="NewPass456",
        confirm_password="NewPass456"
    )
    assert data.new_password == "NewPass456"


def test_password_change_too_short():
    """新密码少于 8 字符应该报错"""
    with pytest.raises(Exception):
        PasswordChange(
            old_password="OldPass123",
            new_password="Ab1",
            confirm_password="Ab1"
        )


def test_password_change_no_uppercase():
    """缺大写字母应该报错"""
    with pytest.raises(Exception):
        PasswordChange(
            old_password="OldPass123",
            new_password="alllower123",
            confirm_password="alllower123"
        )


def test_password_change_no_digit():
    """缺数字应该报错"""
    with pytest.raises(Exception):
        PasswordChange(
            old_password="OldPass123",
            new_password="NoDigitHere",
            confirm_password="NoDigitHere"
        )


def test_password_change_mismatch():
    """new_password 和 confirm_password 不匹配应该报错"""
    with pytest.raises(Exception):
        PasswordChange(
            old_password="OldPass123",
            new_password="NewPass456",
            confirm_password="DifferentOne"
        )


def test_password_change_new_equals_old():
    """新密码不能等于旧密码 (符合安全最佳实践)"""
    with pytest.raises(Exception):
        PasswordChange(
            old_password="SamePass123",
            new_password="SamePass123",
            confirm_password="SamePass123"
        )


# -------------------- UserProfile schema --------------------

def test_user_profile_with_calculations_count():
    """UserProfile 应该包含 total_calculations 字段 (Innovation feature)"""
    from datetime import datetime, timezone
    profile = UserProfile(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at=datetime.now(timezone.utc),
        total_calculations=5
    )
    assert profile.total_calculations == 5


def test_user_profile_default_calculations_zero():
    """新用户的 total_calculations 默认值是 0"""
    from datetime import datetime, timezone
    profile = UserProfile(
        id=1,
        username="newuser",
        email="new@example.com",
        created_at=datetime.now(timezone.utc),
    )
    assert profile.total_calculations == 0
