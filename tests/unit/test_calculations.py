
import pytest
from pydantic import ValidationError

from app.schemas import CalculationCreate, CalculationType
from app.calculation_factory import CalculationFactory


def test_add():
    result = CalculationFactory.calculate(
        10, 5, CalculationType.Add
    )
    assert result == 15


def test_subtract():
    result = CalculationFactory.calculate(
        10, 5, CalculationType.Sub
    )
    assert result == 5


def test_multiply():
    result = CalculationFactory.calculate(
        10, 5, CalculationType.Multiply
    )
    assert result == 50


def test_divide():
    result = CalculationFactory.calculate(
        10, 5, CalculationType.Divide
    )
    assert result == 2


def test_divide_by_zero():
    with pytest.raises(ValueError):
        CalculationFactory.calculate(
            10, 0, CalculationType.Divide
        )


def test_valid_calculation_schema():
    calculation = CalculationCreate(
        a=10, b=5, type="Add"
    )
    assert calculation.type == CalculationType.Add


def test_invalid_calculation_type():
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10, b=5, type="Invalid"
        )


def test_schema_divide_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10, b=0, type="Divide"
        )
