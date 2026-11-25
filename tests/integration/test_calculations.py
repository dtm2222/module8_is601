from fastapi.testclient import TestClient
from main import app
from app.database import Base, get_db
import os

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
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

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


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


def test_calculation_bread(client, db):
    # Add
    response = client.post("/calculations", json={
        "a": 10,
        "b": 5,
        "type": "Add"
    })

    assert response.status_code == 201
    calculation_id = response.json()["id"]

    try:
        assert response.json()["result"] == 15

        # Browse
        response = client.get("/calculations")
        assert response.status_code == 200
        assert any(
            item["id"] == calculation_id
            for item in response.json()
        )

        # Read
        response = client.get(
            f"/calculations/{calculation_id}"
        )
        assert response.status_code == 200
        assert response.json()["result"] == 15

        # Edit
        response = client.put(
            f"/calculations/{calculation_id}",
            json={
                "a": 20,
                "b": 5,
                "type": "Multiply"
            }
        )

        assert response.status_code == 200
        assert response.json()["result"] == 100

        # Verify database update
        db.expire_all()
        saved = db.get(Calculation, calculation_id)
        assert saved.result == 100
        assert saved.type == "Multiply"

        # Delete
        response = client.delete(
            f"/calculations/{calculation_id}"
        )
        assert response.status_code == 204

        # Verify deletion
        response = client.get(
            f"/calculations/{calculation_id}"
        )
        assert response.status_code == 404

    finally:
        db.rollback()
        remaining = db.get(Calculation, calculation_id)
        if remaining is not None:
            db.delete(remaining)
            db.commit()

def test_api_invalid_calculation_type(client):
    response = client.post("/calculations", json={
        "a": 10,
        "b": 5,
        "type": "Invalid"
    })

    assert response.status_code == 400
    assert "error" in response.json()


def test_api_division_by_zero(client):
    response = client.post("/calculations", json={
        "a": 10,
        "b": 0,
        "type": "Divide"
    })

    assert response.status_code == 400
    assert "error" in response.json()


def test_api_calculation_not_found(client):
    response = client.get("/calculations/-1")

    assert response.status_code == 404
    assert response.json()["error"] == "Calculation not found"