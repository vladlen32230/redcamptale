from pydantic import BaseModel, Field

class SavePut(BaseModel):
    description: str = Field(description="Description of the save.")

class SavePost(BaseModel):
    description: str = Field(description="Description of the save.")
    game_state_id: int = Field(description="ID of the game state.")