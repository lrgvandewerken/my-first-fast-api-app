from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine
from repository.base_repository import BaseRepository
from routers.user_router import UserRouter
from dbmodels.user_model import User

# Database setup
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

# Set engine voor alle repositories (BELANGRIJK: voor lifespan)
BaseRepository.set_engine(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    # Maak tabellen aan bij startup
    SQLModel.metadata.create_all(engine)
    yield
    # Cleanup bij shutdown (optioneel)

app = FastAPI(lifespan=lifespan)

# Initialize router after app creation
user_router_instance = UserRouter()
app.include_router(user_router_instance.router, prefix="/user", tags=["users"])

