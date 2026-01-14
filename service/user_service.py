from fastapi import HTTPException

from apimodels.api_user import APIUser
from apimodels.api_user_response import APIUserResponse
from dbmodels import DbUser
from mapper.user_mapper import UserMapper
from repository.user_repository import UserRepository


class UserService():
    def __init__(self):
        pass

    @classmethod
    def create_user(cls, api_user: APIUser) -> APIUserResponse:
        db_user: DbUser = UserMapper.api_user_to_user(api_user)
        saved_user = UserRepository.create(db_user)
        return UserMapper.user_to_api_user_response(saved_user)

    @classmethod
    def get_all_users(cls) -> list[APIUserResponse]:
        users = UserRepository.get_all_users()
        return [UserMapper.user_to_api_user_response(user) for user in users]

