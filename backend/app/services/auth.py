import hashlib
import secrets

from sqlalchemy.orm import Session

from app.models.user import SessionToken, User


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_session_token(db: Session, user: User) -> str:
    token = secrets.token_hex(32)
    db.add(SessionToken(token=token, user_id=user.id))
    db.commit()
    return token


def get_user_by_token(db: Session, token: str) -> User | None:
    session = db.get(SessionToken, token)
    return session.user if session else None
