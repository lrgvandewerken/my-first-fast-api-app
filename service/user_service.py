from apimodels.api_user import APIUser
from mapper.user_mapper import UserMapper
from repository.user_repository import UserRepository


class UserService():
    def __init__(self):
        pass

    def create_user(api_user: APIUser):
        db_user = UserMapper.mapToDbUser(api_user)
        UserRepository.create_user_entity(db_user)
