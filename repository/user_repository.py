from sqlmodel import Session, select
from sqlalchemy import Engine
from dbmodels.user_model import User

class UserRepository():
    def __init__(self):
        pass

    # def create_user_entity(dbuser: DBUser):
    #     print (f" {dbuser.name} has ben added to the repository")

    _engine: Engine | None = None

    @classmethod
    def set_engine(cls, engine: Engine):
        """Set de database engine voor de repository"""
        cls._engine = engine

    @classmethod
    def _get_session(cls) -> Session:
        """Haal database sessie op"""
        if cls._engine is None:
            raise RuntimeError("Database engine niet ingesteld. Roep UserRepository.set_engine() eerst aan.")
        return Session(cls._engine)

    @classmethod
    def create(cls, user: User) -> User:
        """Maak nieuwe user aan"""
        with cls._get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user





