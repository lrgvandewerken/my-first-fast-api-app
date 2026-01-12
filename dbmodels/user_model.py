from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """User entity voor database"""
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str