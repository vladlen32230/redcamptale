from pydantic import BaseModel, Field
from src.schemas.database import Message
from src.schemas.other import Language
from src.schemas.states.characters import Character
from src.schemas.states.locations import Location
from src.schemas.states.times import Time
from src.schemas.states.music import Music

class InteractionPost(BaseModel):
    user_interaction: bool = Field(description="Whether user wants to send his message or request other chracter's message.")
    user_text: str | None = Field(example="Hello, how are you?")
    language: Language = Field(description="Language of the message.")

class CharacterSpriteURLS(BaseModel):
    pose_url: str = Field(description="URL of the character's pose.")
    clothes_url: str = Field(description="URL of the character's clothes.")
    facial_expression_url: str = Field(description="URL of the character's facial expression.")

class MessageGameState(BaseModel):
    message: Message = Field(description="Message.")
    game_state_id: int = Field(description="ID of the game state.")

class GameStateInterface(BaseModel):
    id: int = Field(description="ID of the game state.")
    characters: list[CharacterSpriteURLS] = Field(description="List of characters in the game state.")
    background_url: str = Field(description="URL of the background.")
    followers_head_urls: list[str] = Field(description="List of followers head URLs.")

    time: Time = Field(description="Time of the game state.")

    message: MessageGameState | None

    music_urls: list[str] = Field(description="List of music URLs.")
    music_type: Music = Field(description="Type of the music.")

class CharacterMapLocation(BaseModel):
    location: Location = Field(description="Location of the character.")
    character: Character = Field(description="Character name.")
    character_head_url: str = Field(description="URL of the character's head.")