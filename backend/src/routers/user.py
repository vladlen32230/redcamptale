from fastapi import APIRouter, Depends, HTTPException, status, Body
from src.schemas.api.user import UserPost, JWT, JWTPayload, UserPut
from fastapi.security import OAuth2PasswordRequestForm
from src.auxiliary.config import SECRET_KEY, ALGORITHM, pwd_context
from src.auxiliary.dependencies import get_current_user
from src.db import get_session
from src.schemas.database import User
import jwt
from src.classifier.translator import translator
from sqlmodel import select
from src.auxiliary.database import delete_user, truncate_user
from src.schemas.other import Language
from src.schemas.states.characters import Character

user_router = APIRouter(tags=["user"])

@user_router.post(
    "/user", 
    response_model=None, 
    status_code=201, 
    responses={
        409: {'description': 'User already exists'}
    }
)
async def create_user(
    user_post: UserPost
):
    """
    Creates a new user. IP address will be set to none if user is already in database with this IP.
    Password will be hashed. Name will be checked on uniqueness.
    """
    
    # Hash the password
    hashed_password = pwd_context.hash(user_post.password)

    if user_post.language == Language.ENGLISH:
        name = user_post.game_name
        description = user_post.game_biography
        russian_name = None
        russian_description = None
    elif user_post.language == Language.RUSSIAN:
        name, _, __ = await translator.translate_ru_to_en(
            user_post.game_name,
            character=Character.MAIN_CHARACTER,
            use_premium=True
        )
        description, _, __ = await translator.translate_ru_to_en(
            user_post.game_biography,
            character=Character.MAIN_CHARACTER,
            use_premium=True
        )
        russian_name = user_post.game_name
        russian_description = user_post.game_biography
    
    # Create new user
    new_user = User(
        name=user_post.name,
        password=hashed_password,
        ip_address=None,
        user_biography_name=name,
        user_biography_description=description,
        user_biography_russian_name=russian_name,
        user_biography_russian_description=russian_description
    )
    
    with get_session() as session:
        # Check if user with same name already exists
        existing_user = session.exec(select(User).filter(User.name == user_post.name)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this name already exists"
            )

        # Add user to database
        session.add(new_user)


@user_router.post(
    "/user/login",
    response_model=JWT,
    status_code=200,
    responses={
        401: {'description': 'Invalid credentials'}
    }
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Logs in a user. Returns JWT with user id.
    """
    with get_session() as session:
        # First find the user by username
        user = session.exec(select(User).filter(User.name == form_data.username)).first()
        
        # If user not found or password doesn't verify, return unauthorized
        if not user or not pwd_context.verify(form_data.password, user.password):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create a JWT payload and convert to token
        payload = JWTPayload(sub=str(user.id))
        token = jwt.encode(payload.model_dump(), SECRET_KEY, algorithm=ALGORITHM)
        
        return JWT(access_token=token, token_type="bearer")


@user_router.put(
    "/user",
    response_model=User,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'User not found'}
    }
)
async def update_user(
    user: User = Depends(get_current_user),
    user_put: UserPut = Body(...)
):
    """
    Update the current user account. Requires authentication.
    """
    if user_put.language == Language.ENGLISH:
        name = user_put.game_name
        description = user_put.game_biography

        russian_name = None
        russian_description = None
    elif user_put.language == Language.RUSSIAN:
        name, _, __ = await translator.translate_ru_to_en(
            user_put.game_name,
            character=Character.MAIN_CHARACTER, 
            use_premium=True
        )
        description, _, __ = await translator.translate_ru_to_en(
            user_put.game_biography,
            character=Character.MAIN_CHARACTER,
            use_premium=True
        )

        russian_name = user_put.game_name
        russian_description = user_put.game_biography

    with get_session() as session:
        user.user_biography_name = name
        user.user_biography_description = description

        user.user_biography_russian_name = russian_name
        user.user_biography_russian_description = russian_description

        session.add(user)
        session.flush()
        session.refresh(user)

        return user.model_dump(exclude={"password"})


@user_router.delete(
    "/user",
    response_model=None,
    status_code=204,
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def delete_user_endpoint(
    user: User = Depends(get_current_user)
):
    """
    Delete the current user account. Requires authentication.
    """
    delete_user(user)


@user_router.get(
    "/user/me",
    response_model=User,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def get_current_user_endpoint(
    user: User = Depends(get_current_user)
):
    return user.model_dump(exclude={"password"})


@user_router.post(
    "/user/truncate",
    response_model=None,
    status_code=204,
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def truncate_user_endpoint(
    user: User = Depends(get_current_user)
):
    truncate_user(user)