from sqlmodel import Session
from sqlalchemy import Engine


class BaseRepository:
    """Base repository class that handles database engine management"""
    
    _engine: Engine | None = None

    @classmethod
    def set_engine(cls, engine: Engine):
        """Set de database engine voor alle repositories"""
        cls._engine = engine

    @classmethod
    def _get_session(cls) -> Session:
        """Haal database sessie op"""
        if cls._engine is None:
            raise RuntimeError("Database engine niet ingesteld. Roep BaseRepository.set_engine() eerst aan.")
        return Session(cls._engine)

