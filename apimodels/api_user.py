from pydantic import BaseModel


class APIUser(BaseModel):
    name: str
    email: str



