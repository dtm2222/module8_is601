
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.security import hash_password


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
