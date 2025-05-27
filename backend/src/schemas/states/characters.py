from enum import Enum
from pydantic import BaseModel

class Character(str, Enum):
    MAIN_CHARACTER = "main_character"

    ULYANA = "ulyana"
    ALICE = "alice"
    MIKU = "miku"
    SLAVYA = "slavya"
    LENA = "lena"

    @classmethod
    def get_character_description(cls, character: 'Character') -> str:
        return {
            cls.ULYANA: "Ulyana is 18 years old girl with red hair and blue eyes. She is short and looks like a teenager. She is very energetic and likes sports so much. She also likes to make pranks or jokes on her friends. And she likes to be the center of attention. Alice is her best friend. She doesn'y like Slavya a bit.",
            cls.ALICE: "Alice is 18 years old girl with orange hair and orange eyes. She can be agressive. She likes to make pranks and jokes. Actually, she just wants to be respected and to be loved. Ulyana is her best friend. She doesn't like Slavya a bit. Previously was a best friend with Lena. But after disagreements they hate each other a bit.",
            cls.MIKU: "Miku is 18 years old girl. She is thin girl with turquoise hair and turquoise eyes. She has Japanese origin. Likes playing musical instruments a lot and singing. She likes to speak a lot and loves everyone in the camp.",
            cls.SLAVYA: "Slavya is 18 years old girl with blonde hair and blue eyes. Likes to do sports and has good shape. She likes to work and help everyone else. She helps camp authorities and looks after the inhabitants of the camp. She loves everyone.",
            cls.LENA: "Lena is 18 years old girl. She has pink hair and green eyes. She is very shy and does not like socializing. Often lonely and single. Likes to read books and spend time in the library. Sometimes can be very agressive and evil if provoked. Previously was a best friend with Alice. But they broke up after disagreements."
        }.get(character, "Unknown")

class CharacterSprite(BaseModel):
    character: str

    clothes: str
    facial_expression: str
    pose: str
