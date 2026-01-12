from fastapi import FastAPI
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from repositories.user_repository import UserRepository
from routers.user_router import UserRouter

app.include_router(user_router_instance.router, prefix ="/user", tags=["users"])

app = FastAPI()

user_router_instance = UserRouter()

# Database setup
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=True)

# Set engine voor repository (BELANGRIJK: voor lifespan)
UserRepository.set_engine(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    # Maak tabellen aan bij startup
    SQLModel.metadata.create_all(engine)
    yield
    # Cleanup bij shutdown (optioneel)

app = FastAPI(lifespan=lifespan)

