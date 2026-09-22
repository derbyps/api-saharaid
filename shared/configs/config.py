from datetime import datetime

from pytz import timezone
from sqlalchemy.orm import DeclarativeBase, Session

from shared.models.user import User

from .db import db

TIMESTAMP = datetime.now(timezone("Asia/Makassar")).strftime("%Y-%m-%d %H:%M:%S")
USER_ID = 0


class Base(DeclarativeBase):
    pass


class Config:
    def __init__(self):
        self._session: Session | None = None

    def init(self, event: dict) -> None:
        """init TIMESTAMP, WORKSPACE_ID, USER_ID"""

        db.init()

        global TIMESTAMP, USER_ID

        # timestamp
        custom_timestamp = event.get("timestamp")
        if custom_timestamp:
            TIMESTAMP = custom_timestamp

        else:
            TIMESTAMP = datetime.now(timezone("Asia/Makassar")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        user_id = event.get("user_id")
        if user_id:
            USER_ID = user_id

        else:
            user_email = (
                event.get("requestContext", {})
                .get("authorizer", {})
                .get("claims", {})
                .get("email", "")
            ) or ""

            user = db.session.query(User).filter(User.email == user_email).first()

            if user:
                USER_ID = user.id


config = Config()
