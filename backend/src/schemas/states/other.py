from pydantic import BaseModel
from src.schemas.states.characters import Character
from src.schemas.states.locations import Location
from enum import Enum

class CharacterLocation(BaseModel):
    location: str
    character: str
    clothes: str