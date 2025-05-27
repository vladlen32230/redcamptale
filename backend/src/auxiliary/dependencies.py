from fastapi import Request, Depends
from typing import Optional
import jwt
from src.auxiliary.config import oauth2_scheme, SECRET_KEY, ALGORITHM
from src.db import get_session
from src.schemas.database import User
from sqlmodel import select

# Dependency to get client IP address
def get_client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None

# Dependency to get current user ID from JWT token
def get_current_user_id(token: Optional[str] = Depends(oauth2_scheme)) -> int | None:
    if token is None:
        return None

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id_str = payload.get("sub")
    user_id = int(user_id_str)

    return user_id

def get_current_user(
    user_id: int | None = Depends(get_current_user_id),
    client_ip: str | None = Depends(get_client_ip)
) -> User | None:
    with get_session() as session:
        user = None

        if user_id is not None:
            user = session.exec(select(User).filter(User.id == user_id)).first()
    
        if user is None and client_ip is not None:
            user = session.exec(select(User).filter(User.ip_address == client_ip)).first()

        if user is None and client_ip is not None:
            user = User(
                ip_address=client_ip,
                user_biography_name="Vlad",
                user_biography_description="18 years old guy. He is charismatic and is in a good shape and very beautiful",
                user_biography_russian_name="Влад",
                user_biography_russian_description="18 летний парень. Он харизматичен и в хорошей форме. Он красивый"
            )

            session.add(user)
            session.flush()
            session.refresh(user)
            
        # If we found a user, make sure all attributes are loaded before the session closes
        if user is not None:
            # Expunge the object from the session so it can be used after the session is closed
            session.expunge(user)

        return user