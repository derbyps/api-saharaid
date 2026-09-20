import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        os.environ["DATABASE_URL"],
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"options": "-c timezone=Asia/Jakarta"},
    )
    return sessionmaker(engine, expire_on_commit=False)


class Database:
    def __init__(self):
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Database session is not open")
        return self._session

    def open(self) -> None:
        if self._session is not None:
            raise RuntimeError("Database session is already open")
        self._session = _session_factory()()

    def close(self) -> None:
        if self._session is not None:
            self._session.rollback()
            self._session.close()
            self._session = None


db = Database()
