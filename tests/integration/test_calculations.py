
import os

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Calculation
from app.schemas import CalculationCreate, CalculationType, CalculationRead
from app.calculation_factory import CalculationFactory


TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

if not TEST_DATABASE_URL.endswith("/fastapi_test_db"):
    raise RuntimeError("Tests must use fastapi_test_db")

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_save_calculation(db):
    data = CalculationCreate(a=10, b=5, type="Add")

    result = CalculationFactory.calculate(
        data.a, data.b, data.type
    )

    calculation = Calculation(
        a=data.a,
        b=data.b,
        type=data.type.value,
        result=result
    )

    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    try:
        assert calculation.id is not None
        assert calculation.result == 15

        saved = db.execute(
            select(Calculation).where(
                Calculation.id == calculation.id
            )
        ).scalar_one()

        assert saved.a == 10
        assert saved.b == 5
        assert saved.type == "Add"
        assert saved.result == 15

        output = CalculationRead.model_validate(saved)
        assert output.id == calculation.id
        assert output.result == 15
    finally:
        db.delete(calculation)
        db.commit()


def test_invalid_calculation_type():
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10,
            b=5,
            type="Invalid"
        )


def test_division_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10,
            b=0,
            type="Divide"
        )


def test_save_division(db):
    data = CalculationCreate(a=20, b=4, type="Divide")

    result = CalculationFactory.calculate(
        data.a, data.b, data.type
    )

    calculation = Calculation(
        a=data.a,
        b=data.b,
        type=data.type.value,
        result=result
    )

    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    try:
        assert calculation.id is not None
        assert calculation.result == 5

        saved = db.get(Calculation, calculation.id)

        assert saved is not None
        assert saved.type == "Divide"
        assert saved.result == 5
    finally:
        db.delete(calculation)
        db.commit()
