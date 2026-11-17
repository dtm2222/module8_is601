
from app.schemas import CalculationType


class CalculationFactory:

    @staticmethod
    def calculate(a: float, b: float, type: CalculationType) -> float:

        if type == CalculationType.Add:
            return a + b

        elif type == CalculationType.Sub:
            return a - b

        elif type == CalculationType.Multiply:
            return a * b

        elif type == CalculationType.Divide:
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b

        else:
            raise ValueError("Invalid calculation type")
