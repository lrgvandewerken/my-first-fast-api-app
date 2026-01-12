from sqlmodel import select
from dbmodels.user_model import User
from repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository voor User data access"""
    
    def __init__(self):
        pass

    # def create_user_entity(dbuser: DBUser):
    #     print (f" {dbuser.name} has ben added to the repository")

    @classmethod
    def create(cls, user: User) -> User:
        """Maak nieuwe user aan"""
        with cls._get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user





