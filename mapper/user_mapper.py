from apimodels.api_user import APIUser
from apimodels.db_user import DBUser


class UserMapper():
    def __init__(self):
        pass

    def mapToDbUser(api_user: APIUser):
        dbUser = DBUser(name=api_user.name, password=api_user.password )
        return dbUser


