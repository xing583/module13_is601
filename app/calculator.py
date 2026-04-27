from enum import Enum
from abc import ABC, abstractmethod

class CalculationType(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

class Operation(ABC):
    @abstractmethod
    def calculate(self, a: float, b: float) -> float:
        pass

class Add(Operation):
    def calculate(self, a: float, b: float) -> float:
        return a + b

class Subtract(Operation):
    def calculate(self, a: float, b: float) -> float:
        return a - b

class Multiply(Operation):
    def calculate(self, a: float, b: float) -> float:
        return a * b

class Divide(Operation):
    def calculate(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class CalculationFactory:
    _operations = {
        CalculationType.ADD: Add,
        CalculationType.SUBTRACT: Subtract,
        CalculationType.MULTIPLY: Multiply,
        CalculationType.DIVIDE: Divide,
    }

    @staticmethod
    def create(calc_type: CalculationType) -> Operation:
        operation_class = CalculationFactory._operations.get(calc_type)
        if not operation_class:
            raise ValueError(f"Unknown operation: {calc_type}")
        return operation_class()
