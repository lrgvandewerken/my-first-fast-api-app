from typing import List
from dbmodels.user_model import DbUser
from repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository voor User data access"""
    
    def __init__(self):
        pass

    @classmethod
    def create(cls, user: DbUser) -> DbUser:
        """Maak nieuwe user aan"""
        with cls._get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def get_all_users(cls) -> List[DbUser]:
        with cls._get_session() as session:
            return session.query(DbUser).all()