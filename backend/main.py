from fastapi import FastAPI
from sqlmodel import SQLModel
from src.schemas.database import (
    User, UserDailyUsage, Environment, MapState, 
    Message, GameState, Save
)
from contextlib import asynccontextmanager
from src.routers.game_state import game_state_router
from src.routers.user import user_router
from src.routers.save import save_router
from src.db import engine
from fastapi.middleware.cors import CORSMiddleware
from src.classifier.bert import classifier as bert_classifier

@asynccontextmanager
async def lifespan(app: FastAPI):    
    bert_classifier.load_model()
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan, root_path="/api/v1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_state_router)
app.include_router(user_router)
app.include_router(save_router)