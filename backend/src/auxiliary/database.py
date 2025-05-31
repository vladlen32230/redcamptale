from src.schemas.database import Message, GameState, User, MapState, Environment, UserDailyUsage, SubscriptionTier
from src.db import get_session
from sqlmodel import select, delete
from sqlalchemy import text, desc
from src.auxiliary.state import generate_character_locations
from src.schemas.states.times import Time
from src.auxiliary.state import parse_game_to_interface
from src.schemas.api.game_state import GameStateInterface, MessageGameState
from src.schemas.states.characters import Character
from src.auxiliary.helper import str_to_enum
from datetime import datetime, UTC

def get_last_message_by_state(game_state: GameState) -> Message | None:
    with get_session() as session:
        message = session.exec(
            select(Message).filter(Message.id == game_state.last_message_id)
        ).first()

        if message is not None:
            session.expunge(message)

        return message


def get_user_game_state_by_id(game_state_id: int, user: User) -> GameState | None:
    with get_session() as session:
        game_state = session.exec(
            select(GameState).filter(GameState.id == game_state_id, GameState.user_id == user.id)
        ).first()

        if game_state is not None:
            session.expunge(game_state)

        return game_state


def get_map_state_by_game_state(game_state: GameState) -> MapState:
    with get_session() as session:
        game_state = session.exec(
            select(MapState).where(game_state.map_state_id == MapState.id)
        ).first()

        session.expunge(game_state)
        return game_state


def get_environment_by_game_state(game_state: GameState) -> Environment:
    with get_session() as session:
        environment = session.exec(
            select(Environment).where(game_state.environment_id == Environment.id)
        ).first()

        session.expunge(environment)
        return environment


def get_messages_of_game_state(game_state: GameState, limit: int | None = None, offset: int = 0) -> list[Message]:
    with get_session() as session:
        if game_state.last_message_id is None:
            return []
            
        # Use a recursive CTE to fetch all messages in the chain
        # This is more efficient than fetching them one by one
        query = """
        WITH RECURSIVE message_chain AS (
            SELECT * FROM messages WHERE id = :last_message_id
            UNION ALL
            SELECT m.* FROM messages m
            JOIN message_chain mc ON m.id = mc.previous_message_id
            WHERE m.id IS NOT NULL
        )
        SELECT id FROM message_chain
        """
        
        # Prepare parameters for the query
        params = {"last_message_id": game_state.last_message_id}

        if limit is not None:
            query += "\nLIMIT :limit"
            params["limit"] = limit

        # Execute the raw SQL query to get just the IDs
        result = session.exec(text(query), params=params)
        message_ids = [row[0] for row in result]
        
        # Fetch all messages at once using SQLAlchemy ORM
        if message_ids:
            messages = session.exec(
                select(Message).where(Message.id.in_(message_ids)).order_by(desc(Message.id)).offset(offset)
            ).all()
            
            # Detach all messages from the session
            session.expunge_all()
                
            return messages
        return []


def create_new_game(user: User) -> GameStateInterface:
    with get_session() as session:
        random_locations = generate_character_locations(time=Time.DAY)

        new_environment = Environment()
        new_map_state = MapState(
            time=Time.DAY,
            character_location=random_locations
        )

        session.add(new_environment)
        session.add(new_map_state)
        session.flush()

        session.refresh(new_environment)
        session.refresh(new_map_state)

        new_game_state = GameState(
            user_id=user.id,
            last_message_id=None,
            environment_id=new_environment.id,
            map_state_id=new_map_state.id,
            previous_game_state_id=None
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
    

def change_previous_game_state_links(game_state: GameState, change: int) -> None:
    """
    Use a recursive CTE to find all previous GameStates (by previous_game_state_id),
    including the given one, and change their 'links' field by the `change` amount.
    """
    with get_session() as session:
        # Recursive CTE to get all previous game_state ids
        query = """
        WITH RECURSIVE state_chain AS (
            SELECT id, previous_game_state_id FROM game_states WHERE id = :start_id
            UNION ALL
            SELECT gs.id, gs.previous_game_state_id FROM game_states gs
            JOIN state_chain sc ON gs.id = sc.previous_game_state_id
            WHERE gs.id IS NOT NULL
        )
        SELECT id FROM state_chain
        """
        params = {"start_id": game_state.id}
        result = session.exec(text(query), params=params)
        state_ids = [row[0] for row in result]
        if not state_ids:
            return
        # Fetch all GameState objects at once
        states = session.exec(select(GameState).where(GameState.id.in_(state_ids))).all()
        for state in states:
            state.links += change
            session.add(state)
        
        session.flush()

def get_messages_with_game_state(game_state: GameState, offset: int, limit: int) -> list[MessageGameState]:
    """
    For the given game_state, find all game states in its chain, and for each game state,
    get its associated message if last_message_id is not null. Return a paginated
    list of MessageGameState objects. Pagination is applied to the game state chain.
    """
    with get_session() as session:
        # Step 1: Get a page of game state objects in the chain (pagination here)
        query = """
        WITH RECURSIVE game_state_chain AS (
            SELECT * FROM game_states WHERE id = :game_state_id
            UNION ALL
            SELECT gs.* FROM game_states gs
            JOIN game_state_chain gsc ON gs.id = gsc.previous_game_state_id
            WHERE gs.id IS NOT NULL
        )
        SELECT * FROM game_state_chain
        LIMIT :limit OFFSET :offset
        """
        params = {"game_state_id": game_state.id, "limit": limit, "offset": offset}
        result = session.exec(text(query), params=params)
        # Convert result to GameState objects
        game_states = [GameState.model_validate(row) for row in result.mappings()]
        if not game_states:
            return []
        
        # Step 2: Get the message IDs that are not null
        message_ids = [gs.last_message_id for gs in game_states if gs.last_message_id is not None]
        if not message_ids:
            return []
            
        # Step 3: Fetch all messages at once
        messages = session.exec(
            select(Message)
            .where(Message.id.in_(message_ids))
        ).all()

        session.expunge_all()
        
        # Step 4: Create a dictionary to map message IDs to messages
        for message in messages:
            message.character = str_to_enum(message.character, Character)

        msg_dict = {msg.id: msg for msg in messages}
        
        # Step 5: Build MessageGameState objects
        result = []
        for gs in game_states:
            if gs.last_message_id is not None and gs.last_message_id in msg_dict:
                result.append(MessageGameState(message=msg_dict[gs.last_message_id], game_state_id=gs.id))

        return result


def get_user_current_game_state(user: User) -> GameState | None:
    with get_session() as session:
        game_state = session.exec(
            select(GameState).filter(GameState.id == user.last_game_state_id)
        ).first()
        
        if game_state is not None:
            session.expunge(game_state)

        return game_state


def truncate_user(user: User) -> None:
    """Delete all database rows associated with a user except for usage data.
    
    This function deletes:
    - All GameStates associated with the user.
    - All Saves associated with the user (deletion cascades from GameStates, as Save.game_state_id has ON DELETE CASCADE).
    - All Environments directly linked to these GameStates.
    - All MapStates directly linked to these GameStates.
    - All Messages belonging to the chains initiated by these GameStates.
    
    It does NOT delete:
    - The User record itself
    - UserDailyUsage records
    """
    # Store the user ID since the user object might be detached
    user_id = user.id
    
    with get_session() as session:
        # Get a fresh copy of the user that's attached to the session
        session_user = session.exec(select(User).where(User.id == user_id)).first()
        if not session_user:
            return  # User not found in database
            
        # Reset user's last_game_state_id to None
        session_user.last_game_state_id = None
        session.add(session_user)
        session.flush()

        # Step 1: Get all GameStates for the user and collect associated IDs
        game_states_for_user = session.exec(
            select(GameState).where(GameState.user_id == user_id)
        ).all()

        if not game_states_for_user:
            # If no game states, still commit the change to user.last_game_state_id
            return

                # Collect unique IDs for related entities that need explicit deletion
        env_ids_to_delete = list(set(
            gs.environment_id for gs in game_states_for_user if gs.environment_id is not None
        ))
        map_state_ids_to_delete = list(set(
            gs.map_state_id for gs in game_states_for_user if gs.map_state_id is not None
        ))
        
        # Step 2: Get all message IDs directly from the game states' last_message_id.
        # Based on user feedback, it's assumed that all messages to be deleted
        # for this user will be present in this set. Recursive chain discovery is removed.
        message_ids_to_delete = list(set(
            gs.last_message_id for gs in game_states_for_user if gs.last_message_id is not None
        ))
        
        # (The recursive SQL query previously here is now removed)

        # Step 3: Delete game states
        # This will cascade to Saves because Save.game_state_id has ON DELETE CASCADE.
        game_states_delete_stmt = delete(GameState).where(GameState.user_id == user_id)
        session.exec(game_states_delete_stmt)
        
        # Step 4: Delete the messages themselves
        if message_ids_to_delete:
            messages_delete_stmt = delete(Message).where(Message.id.in_(message_ids_to_delete))
            session.exec(messages_delete_stmt)
        
        # Step 5: Explicitly delete Environments associated with the user's game states
        if env_ids_to_delete:
            environments_delete_stmt = delete(Environment).where(Environment.id.in_(env_ids_to_delete))
            session.exec(environments_delete_stmt)

        # Step 6: Explicitly delete MapStates associated with the user's game states
        if map_state_ids_to_delete:
            map_states_delete_stmt = delete(MapState).where(MapState.id.in_(map_state_ids_to_delete))
            session.exec(map_states_delete_stmt)


def delete_user(user: User) -> None:
    # Store the user ID since the user object might be detached
    user_id = user.id
    
    with get_session() as session:
        # First get a fresh copy of the user that's attached to the session
        session_user = session.exec(select(User).where(User.id == user_id)).first()
        if not session_user:
            return  # User not found in database
            
        # First clean up all user-related data
        truncate_user(session_user)
        
        # Delete user daily usage records
        statement = delete(UserDailyUsage).where(UserDailyUsage.user_id == user_id)
        session.exec(statement)
        
        # Delete the user record itself
        statement = delete(User).where(User.id == user_id)
        session.exec(statement)


def get_previous_history_summaries(
    environment: Environment,
    character: Character,
    limit: int | None = None
) -> list[str]:
    """Recursively fetch previous environment summaries where a specified character was present.
    
    Args:
        environment: The starting environment to begin the search from
        character: The character that must be present in the previous environments
        limit: Optional maximum number of summaries to return
        
    Returns:
        A list of environment summaries where the specified character was present
    """
    with get_session() as session:
        # First, get all environment IDs in the chain where the character was present
        # We use a recursive CTE to find all previous environments
        query = """
        WITH RECURSIVE env_chain AS (
            -- Start with the given environment
            SELECT id, previous_environment_id, previous_environment_characters, previous_environment_summary
            FROM environments 
            WHERE id = :env_id
            
            UNION ALL
            
            -- Join with previous environments
            SELECT e.id, e.previous_environment_id, e.previous_environment_characters, e.previous_environment_summary
            FROM environments e
            JOIN env_chain ec ON e.id = ec.previous_environment_id
            WHERE e.id IS NOT NULL
        )
        -- Select environments where the character was present in previous_environment_characters
        -- and the previous environment summary is not null
        SELECT id, previous_environment_summary 
        FROM env_chain
        WHERE previous_environment_summary IS NOT NULL
          AND previous_environment_characters IS NOT NULL
          AND previous_environment_characters::jsonb @> jsonb_build_array(:character_value)
        """
        
        # Add limit if specified
        if limit is not None:
            query += "\nLIMIT :limit"
            
        # Execute the query with parameters
        params = {
            "env_id": environment.id,
            "character_value": character.value,
            "limit": limit
        }
        
        result = session.exec(text(query), params=params)
        
        # Extract summaries from the result
        summaries = [row[1] for row in result if row[1] is not None]
        
    return list(reversed(summaries))


def delete_previous_game_states_with_0_links(game_state: GameState) -> None:
    """
    Recursively fetch current and previous game states from the given game state 
    and delete those that have 0 links, along with their associated messages.
    
    Args:
        game_state: The starting game state to begin the recursive search from
    """
    with get_session() as session:
        # Find all current and previous game states in the chain with 0 links
        query = """
        WITH RECURSIVE state_chain AS (
            -- Start with the given game state
            SELECT * FROM game_states WHERE id = :game_state_id
            
            UNION ALL
            
            -- Recursively get all previous states
            SELECT gs.* FROM game_states gs
            JOIN state_chain sc ON gs.id = sc.previous_game_state_id
            WHERE gs.id IS NOT NULL
        )
        SELECT id, last_message_id FROM state_chain
        WHERE links = 0
        """
        
        params = {"game_state_id": game_state.id}
        result = session.exec(text(query), params=params)
        
        # Get all game states with 0 links and their message IDs
        states_to_delete = []
        message_ids_to_delete = []
        
        for row in result:
            state_id, message_id = row
            states_to_delete.append(state_id)
            if message_id is not None:
                message_ids_to_delete.append(message_id)
        
        # Delete game states with 0 links and their direct messages
        if states_to_delete:
            # Delete messages
            if message_ids_to_delete:
                message_delete = delete(Message).where(Message.id.in_(message_ids_to_delete))
                session.exec(message_delete)
            
            # Delete game states with 0 links
            state_delete = delete(GameState).where(GameState.id.in_(states_to_delete))
            session.exec(state_delete)


def increase_user_daily_usage(
    user: User, 

    interaction_input_tokens: int = 0, 
    interaction_output_tokens: int = 0, 
    interaction_queries: int = 0,

    translation_input_tokens: int = 0,
    translation_output_tokens: int = 0,
    translation_queries: int = 0,

    summarization_input_tokens: int = 0,
    summarization_output_tokens: int = 0,
    summarization_queries: int = 0,

    premium_interaction_input_tokens: int = 0,
    premium_interaction_output_tokens: int = 0,
    premium_interaction_queries: int = 0,

    premium_translation_input_tokens: int = 0,
    premium_translation_output_tokens: int = 0,
    premium_translation_queries: int = 0,

    premium_summarization_input_tokens: int = 0,
    premium_summarization_output_tokens: int = 0,
    premium_summarization_queries: int = 0,
) -> None:
    with get_session() as session:
        # Get today's date in UTC
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Try to find an existing usage record for today
        daily_usage = session.exec(
            select(UserDailyUsage)
            .where(UserDailyUsage.user_id == user.id)
            .where(UserDailyUsage.date == today)
        ).first()
        
        if daily_usage is None:
            # Create a new record if none exists for today
            daily_usage = UserDailyUsage(
                user_id=user.id,
                date=today,
                interaction_input_tokens=interaction_input_tokens,
                interaction_output_tokens=interaction_output_tokens,
                interaction_queries=interaction_queries,
                translation_input_tokens=translation_input_tokens,
                translation_output_tokens=translation_output_tokens,
                translation_queries=translation_queries,
                summarization_input_tokens=summarization_input_tokens,
                summarization_output_tokens=summarization_output_tokens,
                summarization_queries=summarization_queries,
                premium_interaction_input_tokens=premium_interaction_input_tokens,
                premium_interaction_output_tokens=premium_interaction_output_tokens,
                premium_interaction_queries=premium_interaction_queries,
                premium_translation_input_tokens=premium_translation_input_tokens,
                premium_translation_output_tokens=premium_translation_output_tokens,
                premium_translation_queries=premium_translation_queries,
                premium_summarization_input_tokens=premium_summarization_input_tokens,
                premium_summarization_output_tokens=premium_summarization_output_tokens,
                premium_summarization_queries=premium_summarization_queries
            )
        else:
            # Update existing record
            daily_usage.interaction_input_tokens += interaction_input_tokens
            daily_usage.interaction_output_tokens += interaction_output_tokens
            daily_usage.interaction_queries += interaction_queries
            daily_usage.translation_input_tokens += translation_input_tokens
            daily_usage.translation_output_tokens += translation_output_tokens
            daily_usage.translation_queries += translation_queries
            daily_usage.summarization_input_tokens += summarization_input_tokens
            daily_usage.summarization_output_tokens += summarization_output_tokens
            daily_usage.summarization_queries += summarization_queries
            daily_usage.premium_interaction_input_tokens += premium_interaction_input_tokens
            daily_usage.premium_interaction_output_tokens += premium_interaction_output_tokens
            daily_usage.premium_interaction_queries += premium_interaction_queries
            daily_usage.premium_translation_input_tokens += premium_translation_input_tokens
            daily_usage.premium_translation_output_tokens += premium_translation_output_tokens
            daily_usage.premium_translation_queries += premium_translation_queries
            daily_usage.premium_summarization_input_tokens += premium_summarization_input_tokens
            daily_usage.premium_summarization_output_tokens += premium_summarization_output_tokens
            daily_usage.premium_summarization_queries += premium_summarization_queries
        # Save the record
        session.add(daily_usage)


def check_user_premium_status(user: User) -> bool:
    if (
        user.subscription_tier == SubscriptionTier.PREMIUM and 
        user.subscription_ends_at is not None and 
        user.subscription_ends_at.replace(tzinfo=UTC) >= datetime.now(UTC)
    ):
        return True
    
    if user.subscription_tier == SubscriptionTier.PREMIUM:
        with get_session() as session:
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_ends_at = None
            user.subscription_started_at = None

            session.add(user)
            session.flush()
            session.refresh(user)
            session.expunge_all()

    return False