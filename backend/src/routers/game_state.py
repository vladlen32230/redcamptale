from fastapi import APIRouter, Depends, HTTPException, Body
from src.schemas.states.characters import Character, CharacterSprite
from src.schemas.api.game_state import (
    InteractionPost, 
    MessageGameState, 
    GameStateInterface, 
    CharacterMapLocation
)
from src.schemas.other import Language
from src.schemas.states.locations import Location
from src.auxiliary.dependencies import get_current_user
from src.db import get_session
from src.schemas.database import User, GameState, Environment, MapState, Message, SubscriptionTier
from sqlmodel import select
from src.schemas.states.times import Time
from src.auxiliary.helper import str_to_enum
from src.classifier.translator import translator
from src.auxiliary.state import (
    parse_game_to_interface, 
    parse_map_state_to_character_locations,
    get_character_sprites_by_location,
    generate_character_locations,
    next_time_dictionary,
)
from src.classifier.bert import classifier
from src.llm.interaction import (
    get_summary_of_messages, 
    get_character_message
)
from src.schemas.states.other import CharacterLocation
from src.schemas.states.music import Music
from src.schemas.states.entities.alice import AliceClothes
from src.schemas.states.entities.ulyana import UlyanaClothes
from src.schemas.states.entities.slavya import SlavyaClothes
from src.schemas.states.entities.lena import LenaClothes
from src.schemas.states.entities.miku import MikuClothes
from src.auxiliary.database import (
    get_user_game_state_by_id, 
    get_map_state_by_game_state, 
    get_environment_by_game_state,
    get_messages_of_game_state,
    create_new_game,
    get_last_message_by_state,
    change_previous_game_state_links,
    get_messages_with_game_state,
    get_user_current_game_state,
    get_previous_history_summaries,
    delete_previous_game_states_with_0_links,
    increase_user_daily_usage
)

game_state_router = APIRouter(tags=["game_state"])

@game_state_router.get(
    "/game_state/continue",
    response_model=GameStateInterface,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def continue_game(
    user: User = Depends(get_current_user)
):
    """
    Continue the game.
    It will return game state with updated state.
    """
    with get_session() as session:
        if user.last_game_state_id is None:
            return create_new_game(user)

        else:
            last_game_state: GameState = session.exec(select(GameState).filter(GameState.id == user.last_game_state_id)).first()
            environment: Environment = get_environment_by_game_state(last_game_state)
            map_state: MapState = get_map_state_by_game_state(last_game_state)

            last_message = get_last_message_by_state(last_game_state)

            interface = parse_game_to_interface(
                environment=environment,
                game_state=last_game_state,
                map_state=map_state,
                message=last_message
            )

            return interface


@game_state_router.post(
    "/game_state/new",
    response_model=GameStateInterface,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'}
    }
)
async def start_new_game(
    user: User = Depends(get_current_user)
):  
    last_game_state = get_user_game_state_by_id(user.last_game_state_id, user)
    if last_game_state is not None:
        change_previous_game_state_links(last_game_state, change=-1)
        delete_previous_game_states_with_0_links(last_game_state)

    return create_new_game(user)


@game_state_router.post(
    "/game_state/{game_state_id}/interaction",
    response_model=GameStateInterface,
    status_code=200,
    responses={
        400: {'description': 'Free tier usage exceeded'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def interaction(
    interaction_post: InteractionPost,
    game_state_id: int,
    user: User = Depends(get_current_user)
):
    """
    Interaction with the game state.
    User can either ask for character message or send his message.
    Backend will return updated game state.
    It will use text generation and classification methods to determine
    next speaking character, his message, translating to russian, changing music and character sprites.
    """
    use_premium = user.subscription_tier == SubscriptionTier.PREMIUM.value

    translation_input_tokens = 0
    translation_output_tokens = 0
    translation_queries = 0

    interaction_input_tokens = 0
    interaction_output_tokens = 0
    interaction_queries = 0

    game_state = get_user_game_state_by_id(game_state_id, user)

    if game_state is None:
        raise HTTPException(404, detail="Game state not found.")

    new_game_state = game_state

    # Get previous 15 messages from game state
    messages = get_messages_of_game_state(new_game_state, limit=15)
    recent_message = messages[0] if messages else None

    environment = get_environment_by_game_state(game_state)
    map_state = get_map_state_by_game_state(game_state)

    game_state_sprites: list[CharacterSprite] = [CharacterSprite(**c) for c in game_state.characters]

    if not game_state_sprites and not interaction_post.user_interaction:
        return parse_game_to_interface(
            environment=environment,
            game_state=game_state,
            map_state=map_state,
            message=None
        )

    with get_session() as session:
        if interaction_post.user_interaction:
            if not game_state_sprites:
                english_text = interaction_post.user_text
                russian_text = interaction_post.user_text
            elif interaction_post.language == Language.RUSSIAN:
                english_text, input_tokens, output_tokens = await translator.translate_ru_to_en(
                    interaction_post.user_text,
                    Character.MAIN_CHARACTER,
                    use_premium=use_premium
                )

                translation_input_tokens += input_tokens
                translation_output_tokens += output_tokens
                translation_queries += 1

                russian_text = interaction_post.user_text
            else:
                english_text = interaction_post.user_text
                russian_text = None

            new_message = Message(
                character=Character.MAIN_CHARACTER.value,
                english_text=english_text,
                russian_translation=russian_text,
                previous_message_id=recent_message.id if recent_message is not None else None
            )

            session.add(new_message)
            session.flush()
            session.refresh(new_message)

            new_game_state = GameState(
                user_id=user.id,
                characters=game_state.characters,
                music=game_state.music,
                followers=game_state.followers,
                last_message_id=new_message.id,
                environment_id=game_state.environment_id,
                map_state_id=game_state.map_state_id,
                previous_game_state_id=game_state.id
            )

            session.add(new_game_state)
            session.flush()
            session.refresh(new_game_state)

            game_state = new_game_state

            messages = [new_message] + messages
            recent_message = new_message

            if not game_state_sprites:
                user.last_game_state_id = game_state.id
                session.add(user)
                return parse_game_to_interface(
                    environment=environment,
                    game_state=game_state,
                    map_state=map_state,
                    message=recent_message
                )

        # Get all character names from current game state
        character_names = []
        if game_state_sprites:
            character_names = [
                str_to_enum(character.character, Character) for character in game_state_sprites
            ]

        classifiying_messages = messages[:1]

        # DETERMINE NEXT SPEAKER
        next_character = classifier.determine_next_speaking_character(
            messages=classifiying_messages,
            characters=character_names
        )

        clothes = None
        for character in game_state_sprites:
            if character.character == next_character:
                clothes = character.clothes
                break

        character_history = get_previous_history_summaries(
            environment=environment,
            character=next_character,
            limit=6
        )

        time_of_day = str_to_enum(map_state.time, Time)

        # SPEAK
        character_message, input_tokens, output_tokens = await get_character_message(
            character_name=next_character,
            other_character_location=character_names,
            location=str_to_enum(environment.location, Location),
            name_of_main_character=user.user_biography_name,
            time_of_day=time_of_day,
            biography_of_main_character=user.user_biography_description,
            clothes=str_to_enum(clothes, [UlyanaClothes, AliceClothes, SlavyaClothes, LenaClothes, MikuClothes]),
            previous_history="\n\n".join(character_history),
            messages=messages,
            use_premium=use_premium
        )

        interaction_input_tokens += input_tokens
        interaction_output_tokens += output_tokens
        interaction_queries += 1

        russian_translation_message = None
        if interaction_post.language == Language.RUSSIAN:
            russian_translation_message, input_tokens, output_tokens = await translator.translate_en_to_ru(
                character_message,
                next_character,
                use_premium=use_premium
            )

            translation_input_tokens += input_tokens
            translation_output_tokens += output_tokens
            translation_queries += 1

        new_message = Message(
            character=next_character,
            english_text=character_message,
            russian_translation=russian_translation_message,
            previous_message_id=recent_message.id if recent_message is not None else None
        )

        session.add(new_message)
        session.flush()
        session.refresh(new_message)

        new_messages = [new_message] + messages
        new_followers_messages = new_messages[:2]
        new_music_messages = new_messages[:2]

        #DETERMINE MUSIC
        music = classifier.determine_music(
            new_music_messages, 
            str_to_enum(game_state.music, Music)
        )

        #DETERMINE SPRITE
        new_sprite = classifier.determine_next_chracter_sprite(
            chracter_name=next_character,
            character_clothes=clothes,
            messages=[new_message]
        )

        new_sprites = [
            sprite for sprite in game_state_sprites if sprite.character != next_character
        ] + [new_sprite]

        #DETERMINE FOLLOWERS
        new_following=[str_to_enum(follower, Character) for follower in game_state.followers]

        if next_character not in new_following:
            following = classifier.determine_following(
                character=next_character,
                user_character_name=user.user_biography_name,
                messages=new_followers_messages
            )

            if following:
                new_following.append(next_character)

        new_character_game_state = GameState(
            user_id=user.id,
            characters=[sprite.model_dump() for sprite in new_sprites],
            music=music,
            followers=new_following,
            last_message_id=new_message.id,
            environment_id=game_state.environment_id,
            map_state_id=game_state.map_state_id,
            previous_game_state_id=new_game_state.id
        )

        session.add(new_character_game_state)
        session.flush()
        session.refresh(new_character_game_state)

        user.last_game_state_id = new_character_game_state.id
        session.add(user)

        increase_user_daily_usage(
            user=user,
            interaction_input_tokens=interaction_input_tokens,
            interaction_output_tokens=interaction_output_tokens,
            interaction_queries=interaction_queries,
            translation_input_tokens=translation_input_tokens,
            translation_output_tokens=translation_output_tokens,
            translation_queries=translation_queries
        )

        parsed = parse_game_to_interface(
            environment=environment,
            game_state=new_character_game_state,
            map_state=map_state,
            message=new_message
        )

        return(parsed)


@game_state_router.get(
    "/game_state/{game_state_id}",
    response_model=GameStateInterface,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def get_game_state(
    game_state_id: int,
    user: User = Depends(get_current_user)
):
    """
    Get game state by id.
    It will decrease links of previous game states and increase of the new.
    Also it will change head link in user's database row, to refer it later.
    It returns new game state with updated state.
    """
    with get_session() as session:
        game_state = get_user_game_state_by_id(game_state_id, user)
        if not game_state:
            raise HTTPException(404, detail="Game state not found.")

        user_last_game_state = get_user_current_game_state(user)

        user.last_game_state_id = game_state.id
        session.add(user)

        change_previous_game_state_links(game_state, 1)
        
        if user_last_game_state is not None:
            change_previous_game_state_links(user_last_game_state, -1)
            delete_previous_game_states_with_0_links(user_last_game_state)

    return parse_game_to_interface(
        environment=get_environment_by_game_state(game_state),
        game_state=game_state,
        map_state=get_map_state_by_game_state(game_state),
        message=get_last_message_by_state(game_state)
    )


@game_state_router.post(
    "/game_state/{game_state_id}/location",
    response_model=GameStateInterface,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def change_location(
    game_state_id: int,
    new_location: Location = Body(..., embed=True),
    user: User = Depends(get_current_user)
):
    """
    Changes the location.
    It will create new environment and game state.
    Map state will be new only if there is characters that followed user.
    """
    use_premium = user.subscription_tier == SubscriptionTier.PREMIUM.value
    game_state = get_user_game_state_by_id(game_state_id, user)

    if game_state is None:
        raise HTTPException(404, detail="Game state not found.")

    with get_session() as session:
        map_state = get_map_state_by_game_state(game_state)
        environment = get_environment_by_game_state(game_state)
        messages = get_messages_of_game_state(game_state)

        if game_state.followers:
            new_character_locations = []
            for character_location in map_state.character_location:
                character_location = CharacterLocation(**character_location)
                if character_location.character in game_state.followers:
                    new_character_locations.append(
                        CharacterLocation(
                            location=new_location,
                            character=character_location.character,
                            clothes=character_location.clothes
                        ).model_dump()
                    )
                else:
                    new_character_locations.append(
                        character_location.model_dump()
                    )

            new_map_state = MapState(
                time=map_state.time,
                character_location=new_character_locations
            )

            session.add(new_map_state)
            session.flush()
            session.refresh(new_map_state)

            new_map_state_id = new_map_state.id

        else:
            new_character_locations = map_state.character_location
            new_map_state = map_state
            new_map_state_id = map_state.id

        if messages and game_state.characters:
            previous_environment_summary, input_tokens, output_tokens = await get_summary_of_messages(
                messages=messages,
                use_premium=use_premium
            )
            increase_user_daily_usage(
                user=user,
                summarization_input_tokens=input_tokens,
                summarization_output_tokens=output_tokens,
                summarization_queries=1
            )

        else:
            previous_environment_summary = None
        
        new_environment = Environment(
            location=new_location,
            previous_environment_summary=previous_environment_summary,
            previous_environment_characters=[character['character'] for character in game_state.characters],
            previous_environment_id=environment.id
        )

        session.add(new_environment)
        session.flush()
        session.refresh(new_environment)

        character_sprites = get_character_sprites_by_location(
            location=new_location,
            character_locations=new_character_locations
        )

        new_game_state = GameState(
            user_id=user.id,
            characters=character_sprites,
            environment_id=new_environment.id,
            music=Music.NORMAL,
            last_message_id=None,
            map_state_id=new_map_state_id,
            previous_game_state_id=game_state.id
        )

        session.add(new_game_state)
        session.flush()
        session.refresh(new_game_state)

        user.last_game_state_id = new_game_state.id
        session.add(user)

        return parse_game_to_interface(
            environment=new_environment,
            game_state=new_game_state,
            map_state=new_map_state
        )


@game_state_router.post(
    "/game_state/{game_state_id}/map",
    response_model=GameStateInterface,
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def change_map(
    game_state_id: int,
    user: User = Depends(get_current_user)
):
    """
    Changes the map.
    There will be new characters' positions and next time.
    Game state will be created.
    """
    use_premium = user.subscription_tier == SubscriptionTier.PREMIUM.value
    game_state = get_user_game_state_by_id(game_state_id, user)
    messages = get_messages_of_game_state(game_state)
    environment = get_environment_by_game_state(game_state)
    map_state = get_map_state_by_game_state(game_state)

    if messages and game_state.characters:
        previous_environment_summary, input_tokens, output_tokens = await get_summary_of_messages(
            messages=messages,
            use_premium=use_premium
        )
        increase_user_daily_usage(
            user=user,
            summarization_input_tokens=input_tokens,
            summarization_output_tokens=output_tokens,
            summarization_queries=1
        )
    else:
        previous_environment_summary = None

    next_time = next_time_dictionary[map_state.time]
    random_character_locations = generate_character_locations(next_time)

    new_environment = Environment(
        location=Location.MAIN_CHARACTER_HOME,
        previous_environment_summary=previous_environment_summary,
        previous_environment_characters=[character['character'] for character in game_state.characters],
        previous_environment_id=environment.id
    )

    new_map_state = MapState(
        time=next_time,
        character_location=random_character_locations
    )

    with get_session() as session:
        session.add(new_environment)
        session.add(new_map_state)

        session.flush()
        session.refresh(new_environment)
        session.refresh(new_map_state)

        character_sprites = get_character_sprites_by_location(
            location=Location.MAIN_CHARACTER_HOME,
            character_locations=random_character_locations
        )

        new_game_state = GameState(
            user_id=user.id,
            characters=character_sprites,
            environment_id=new_environment.id,
            music=Music.NONE,
            last_message_id=None,
            map_state_id=new_map_state.id,
            previous_game_state_id=game_state.id
        )

        session.add(new_game_state)

        session.flush()
        session.refresh(new_game_state)

        user.last_game_state_id = new_game_state.id
        session.add(user)

        result = parse_game_to_interface(
            environment=new_environment,
            game_state=new_game_state,
            map_state=new_map_state
        )
        
    return result

@game_state_router.get(
    "/game_state/{game_state_id}/map",
    response_model=list[CharacterMapLocation],
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def get_map(
    game_state_id: int,
    user: User = Depends(get_current_user)
):
    """
    Get current map.
    It will have time and characters' positions.
    """
    with get_session() as session:
        game_state = get_user_game_state_by_id(game_state_id, user)

        if game_state is None:
            raise HTTPException(404, detail="Game state not found.")

        map_state: MapState = session.exec(select(MapState).filter(MapState.id == game_state.map_state_id)).first()

        return parse_map_state_to_character_locations(map_state)


@game_state_router.get(
    "/game_state/{game_state_id}/messages",
    response_model=list[MessageGameState],
    status_code=200,
    responses={
        401: {'description': 'Unauthorized'},
        404: {'description': 'Game state not found'}
    }
)
async def get_messages(
    game_state_id: int,
    user: User = Depends(get_current_user),
    offset: int = 0,
    limit: int = 10
):
    """
    Get message history.
    They will have game state id, which can be loaded later.
    """
    game_state = get_user_game_state_by_id(game_state_id, user)
    if not game_state:
        raise HTTPException(404, detail="Game state not found.")

    game_messages = get_messages_with_game_state(game_state, offset, limit)

    return game_messages
