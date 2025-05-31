from fastapi import Depends
from typing import Optional
import jwt
from src.auxiliary.config import oauth2_scheme, SECRET_KEY, ALGORITHM
from src.db import get_session
from src.schemas.database import User
from sqlmodel import select
from fastapi import HTTPException

# Dependency to get current user ID from JWT token
def get_current_user_id(token: Optional[str] = Depends(oauth2_scheme)) -> int | None:
    if token is None:
        return None

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id_str = payload.get("sub")
    user_id = int(user_id_str)

    return user_id

def get_current_user(
    user_id: int | None = Depends(get_current_user_id)
) -> User:
    with get_session() as session:
        user = None

        if user_id is not None:
            user = session.exec(select(User).filter(User.id == user_id)).first()

        if user is None:
            raise HTTPException(401)
        # If we found a user, make sure all attributes are loaded before the session closes
        if user is not None:
            # Expunge the object from the session so it can be used after the session is closed
            session.expunge(user)

        return user