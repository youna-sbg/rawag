import secrets
from collections.abc import Iterator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.config import ADMIN_API_KEY
from app.database import SessionLocal


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


def require_admin(x_api_key: str = Header()) -> None:
    if not secrets.compare_digest(x_api_key.encode(), ADMIN_API_KEY.encode()):
        raise HTTPException(401, "کلید ادمین نامعتبر است")
