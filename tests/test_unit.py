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
