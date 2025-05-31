from sqlmodel import Field as SQLModelField, SQLModel
from datetime import datetime, UTC
from src.schemas.states.locations import Location
from src.schemas.states.times import Time
from src.schemas.states.other import CharacterLocation
from src.schemas.states.music import Music
from src.schemas.states.characters import CharacterSprite
from enum import Enum

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"

class UserDailyUsage(SQLModel, table=True):
    __tablename__ = "user_daily_usage"

    id: int | None = SQLModelField(default=None, primary_key=True)
    user_id: int = SQLModelField(sa_column=Column(ForeignKey("users.id", ondelete="SET NULL")))
    date: datetime = SQLModelField(default=datetime.now(UTC))

    interaction_input_tokens: int = SQLModelField(default=0)
    interaction_output_tokens: int = SQLModelField(default=0)
    interaction_queries: int = SQLModelField(default=0)

    translation_input_tokens: int = SQLModelField(default=0)
    translation_output_tokens: int = SQLModelField(default=0)
    translation_queries: int = SQLModelField(default=0)

    summarization_input_tokens: int = SQLModelField(default=0)
    summarization_output_tokens: int = SQLModelField(default=0)
    summarization_queries: int = SQLModelField(default=0)

    premium_interaction_input_tokens: int = SQLModelField(default=0)
    premium_interaction_output_tokens: int = SQLModelField(default=0)
    premium_interaction_queries: int = SQLModelField(default=0)

    premium_summarization_input_tokens: int = SQLModelField(default=0)
    premium_summarization_output_tokens: int = SQLModelField(default=0)
    premium_summarization_queries: int = SQLModelField(default=0)

    premium_translation_input_tokens: int = SQLModelField(default=0)
    premium_translation_output_tokens: int = SQLModelField(default=0)
    premium_translation_queries: int = SQLModelField(default=0)

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = SQLModelField(default=None, primary_key=True)

    name: str | None = SQLModelField(unique=True)
    password: str | None

    user_biography_name: str
    user_biography_description: str

    user_biography_russian_name: str | None
    user_biography_russian_description: str | None

    subscription_tier: str = SQLModelField(default=SubscriptionTier.FREE.value, sa_column=Column(String))
    subscription_started_at: datetime | None = SQLModelField(default=None)
    subscription_ends_at: datetime | None = SQLModelField(default=None)

    last_game_state_id: int | None = SQLModelField(sa_column=Column(ForeignKey("game_states.id", ondelete="SET NULL")))

    created_at: datetime = SQLModelField(default=datetime.now(UTC))

class Environment(SQLModel, table=True):
    __tablename__ = "environments"

    id: int | None = SQLModelField(default=None, primary_key=True)
    location: str = SQLModelField(default=Location.MAIN_CHARACTER_HOME.value, sa_column=Column(String))

    previous_environment_summary: str | None = SQLModelField(default=None)
    previous_environment_characters: list[str] = SQLModelField(default_factory=list, sa_column=Column(JSON))
    previous_environment_id: int | None = SQLModelField(sa_column=Column(ForeignKey("environments.id", ondelete="CASCADE")))

class MapState(SQLModel, table=True):
    __tablename__ = "map_states"

    id: int | None = SQLModelField(default=None, primary_key=True)
    time: str = SQLModelField(default=Time.DAY.value, sa_column=Column(String))
    character_location: list[CharacterLocation] = SQLModelField(default_factory=list, sa_column=Column(JSON))

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = SQLModelField(default=None, primary_key=True)
    character: str = SQLModelField(sa_column=Column(String))

    english_text: str
    russian_translation: str | None

    previous_message_id: int | None = SQLModelField(sa_column=Column(ForeignKey("messages.id", ondelete="SET NULL")))

class GameState(SQLModel, table=True):
    __tablename__ = "game_states"

    id: int | None = SQLModelField(default=None, primary_key=True)
    user_id: int = SQLModelField(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE")))

    characters: list[CharacterSprite] = SQLModelField(default_factory=list, sa_column=Column(JSON))
    music: str = SQLModelField(default=Music.NONE.value, sa_column=Column(String))

    followers: list[str] = SQLModelField(default_factory=list, sa_column=Column(JSON))

    last_message_id: int | None = SQLModelField(sa_column=Column(ForeignKey("messages.id", ondelete="SET NULL")))
    environment_id: int = SQLModelField(sa_column=Column(ForeignKey("environments.id", ondelete="CASCADE")))
    map_state_id: int = SQLModelField(sa_column=Column(ForeignKey("map_states.id", ondelete="CASCADE")))

    previous_game_state_id: int | None = SQLModelField(sa_column=Column(ForeignKey("game_states.id", ondelete="SET NULL")))

    links: int = SQLModelField(default=1)

class Save(SQLModel, table=True):
    __tablename__ = "saves"

    id: int | None = SQLModelField(default=None, primary_key=True)
    user_id: int = SQLModelField(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE")))

    game_state_id: int = SQLModelField(sa_column=Column(ForeignKey("game_states.id", ondelete="CASCADE")))

    created_at: datetime = SQLModelField(default=datetime.now(UTC))
    description: str = SQLModelField(default="")
