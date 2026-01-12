from pydantic import BaseModel


class APIUser(BaseModel):
    name: str
    password: str