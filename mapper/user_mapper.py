from apimodels.api_user import APIUser
from apimodels.api_user_response import APIUserResponse
from dbmodels import DbUser


class UserMapper():
    def __init__(self):
        pass

    def api_user_to_user(api_user: APIUser):
        return DbUser(name=api_user.name, email=api_user.email )

    @staticmethod
    def user_to_api_user_response(user: DbUser) -> APIUserResponse:
        return APIUserResponse(id=user.id, name=user.name, email=user.email)


