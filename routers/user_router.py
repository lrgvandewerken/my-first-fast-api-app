from fastapi import APIRouter

from apimodels.api_user import APIUser
from mapper.user_mapper import UserMapper
from service.user_service import UserService


class UserRouter:
    router = APIRouter()

    @router.get("/hi")
    def root():
        return {"message": "Hello World"}

    @router.post("/create-user")
    def create_user(api_user: APIUser):
        UserService.create_user(api_user)


