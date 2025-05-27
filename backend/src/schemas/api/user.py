from pydantic import BaseModel, Field
from src.schemas.other import Language

class JWTPayload(BaseModel):
    sub: str 
    
class JWT(BaseModel):
    access_token: str = Field(example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEwLCJpYXQiOjE3MTU4MzM5MjksImV4cCI6MTcxNTgzNzUyOX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    token_type: str = 'Bearer'

class UserPost(BaseModel):
    name: str
    password: str
    game_name: str
    game_biography: str
    language: Language

class UserPut(BaseModel):
    game_name: str
    game_biography: str
    language: Language