import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import Base, get_db
from app.models import User
from app.schemas import UserCreate
from app.crud import create_user
from app.security import verify_password


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


def test_create_user(db):
    unique = uuid.uuid4().hex[:8]
    password = "SecureTest123!"

    user = create_user(
        db,
        UserCreate(
            username=f"user_{unique}",
            email=f"user_{unique}@example.com",
            password=password
        )
    )

    try:
        assert user.id is not None
        assert user.password_hash != password
        assert verify_password(password, user.password_hash)
    finally:
        db.delete(user)
        db.commit()


def test_duplicate_username(db):
    unique = uuid.uuid4().hex[:8]
    username = f"user_{unique}"

    first = create_user(
        db,
        UserCreate(
            username=username,
            email=f"first_{unique}@example.com",
            password="SecureTest123!"
        )
    )

    try:
        with pytest.raises(IntegrityError):
            create_user(
                db,
                UserCreate(
                    username=username,
                    email=f"second_{unique}@example.com",
                    password="SecureTest123!"
                )
            )
    finally:
        db.rollback()
        db.delete(first)
        db.commit()


def test_duplicate_email(db):
    unique = uuid.uuid4().hex[:8]
    email = f"user_{unique}@example.com"

    first = create_user(
        db,
        UserCreate(
            username=f"first_{unique}",
            email=email,
            password="SecureTest123!"
        )
    )

    try:
        with pytest.raises(IntegrityError):
            create_user(
                db,
                UserCreate(
                    username=f"second_{unique}",
                    email=email,
                    password="SecureTest123!"
                )
            )
    finally:
        db.rollback()
        db.delete(first)
        db.commit()

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

def test_register_endpoint(client, db):
    unique = uuid.uuid4().hex[:8]

    payload = {
        "username": f"api_{unique}",
        "email": f"api_{unique}@example.com",
        "password": "SecureTest123!"
    }

    response = client.post("/users/register", json=payload)

    assert response.status_code == 201

    user = db.query(User).filter_by(
        username=payload["username"]
    ).first()

    try:
        assert user is not None
        assert response.json()["username"] == payload["username"]
        assert "password_hash" not in response.json()
        assert user.password_hash != payload["password"]
        assert verify_password(
            payload["password"], user.password_hash
        )
    finally:
        if user is not None:
            db.delete(user)
            db.commit()


def test_login_endpoint(client, db):
    unique = uuid.uuid4().hex[:8]
    password = "SecureTest123!"

    user = create_user(
        db,
        UserCreate(
            username=f"login_{unique}",
            email=f"login_{unique}@example.com",
            password=password
        )
    )

    try:
        response = client.post("/users/login", json={
            "username": user.username,
            "password": password
        })

        assert response.status_code == 200
        assert response.json()["message"] == "Login successful"

        response = client.post("/users/login", json={
            "username": user.username,
            "password": "WrongPassword123!"
        })

        assert response.status_code == 401
        assert response.json()["error"] == "Invalid username or password"
    finally:
        db.delete(user)
        db.commit()