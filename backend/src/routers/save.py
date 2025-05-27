from fastapi import APIRouter, Depends, HTTPException
from src.schemas.database import Save
from src.schemas.api.save import SavePost, SavePut
from src.auxiliary.database import change_previous_game_state_links, get_user_game_state_by_id, delete_previous_game_states_with_0_links
from src.auxiliary.dependencies import get_current_user
from src.db import get_session
from src.schemas.database import User
from sqlmodel import select


save_router = APIRouter(tags=["save"])

@save_router.post(
    "/save",
    response_model=Save,
    status_code=201,
    responses={404: {'description': 'Game state of this user is not found'}}
)
async def create_save(
    save_post: SavePost,
    user: User | None = Depends(get_current_user)
):
    """
    Creates a database entry for a save. 
    Recursively increases links count for previous game states and current.
    Points to game id, which can be loaded later.
    """
    if user is None:
        raise HTTPException(400)

    game_state = get_user_game_state_by_id(save_post.game_state_id, user)
    if game_state is None:
        raise HTTPException(404)

    save = Save(
        user_id=user.id,
        game_state_id=game_state.id,
        description=save_post.description
    )

    with get_session() as session:
        session.add(save)
        session.flush()
        session.refresh(save)

    change_previous_game_state_links(game_state, change=1)

    return save.model_dump()


@save_router.get(
    "/saves",
    response_model=list[Save],
    status_code=200,
    responses={}
)
async def get_saves(
    user: User | None = Depends(get_current_user),
    offset: int = 0,
    limit: int = 10
):
    """
    Returns a list of saves.
    It will have game state id which user can refer to later to load the game state.
    """
    with get_session() as session:
        saves = session.exec(
            select(Save).filter(Save.user_id == user.id).offset(offset).limit(limit)
        ).all()

        return [save.model_dump() for save in saves]


@save_router.put(
    "/save/{save_id}",
    response_model=Save,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Save not found'}
    }
)
async def update_save(
    save_id: int,
    save_put: SavePut,
    user: User | None = Depends(get_current_user)
):
    """
    Updates description of the save.
    """
    with get_session() as session:
        save = session.exec(
            select(Save).filter(Save.id == save_id, Save.user_id == user.id)
        ).first()

        if save is None:
            raise HTTPException(404)

        save.description = save_put.description

        session.add(save)
        session.flush()
        session.refresh(save)

        return save.model_dump()


@save_router.delete(
    "/save/{save_id}",
    response_model=None,
    status_code=204,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def delete_save(
    save_id: int,
    user: User | None = Depends(get_current_user)
):
    """
    Deletes a save. Decreases links count for previous game states and current.
    If links count is 0 of game states, they will be deleted.
    """
    with get_session() as session:
        save = session.exec(
            select(Save).filter(Save.id == save_id, Save.user_id == user.id)
        ).first()

        if save is None:
            raise HTTPException(404)

        game_state = get_user_game_state_by_id(save.game_state_id, user)
        change_previous_game_state_links(game_state, change=-1)
        delete_previous_game_states_with_0_links(game_state)

        session.delete(save)