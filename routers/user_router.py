from typing import List

from fastapi import APIRouter
from apimodels.api_user import APIUser
from apimodels.api_user_response import APIUserResponse
from service.user_service import UserService


class UserRouter:
    router = APIRouter()

    @router.get("/hi")
    def root():
        return {"message": "Hello World"}

    @router.post("/create-user")
    def create_user(api_user: APIUser):
        UserService.create_user(api_user)

    @router.get("/users", response_model=List[APIUserResponse])
    def get_users():
        return UserService.get_all_users()

