import os
import ssl
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.engine.interfaces import DBAPICursor
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

CONNECTION = None
CURSOR: DBAPICursor | None = None

connection = None
cursor: DBAPICursor | None = None


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        URL.create(
            "mysql+pymysql",
            username=os.environ["RDS_USER"],
            password=os.environ["RDS_PASSWORD"],
            host=os.environ["RDS_HOST"],
            database=os.environ["RDS_DATABASE"],
            query={"charset": "utf8mb4"},
        ),
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "init_command": "SET time_zone = '+07:00'",
            "ssl": ssl.create_default_context(),
        },
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

    def commit(self) -> None:
        if self._session is not None:
            self._session.commit()

    def save(self, instance: object) -> None:
        if self._session is not None:
            self._session.add(instance)
            self._session.flush()

    def init(self) -> None:
        global CONNECTION, CURSOR, connection, cursor

        try:
            CONNECTION = self.session.connection().connection
        except:
            self.session.rollback()
            CONNECTION = self.session.connection().connection

        CURSOR = CONNECTION.cursor()
        connection = CONNECTION
        cursor = CURSOR


db = Database()
