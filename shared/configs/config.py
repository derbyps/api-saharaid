from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import DeclarativeBase, Session

from shared.models.user import User

from .db import db

WIB = ZoneInfo("Asia/Jakarta")

TIMESTAMP = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
USER_ID = ""


def get_timestamp(timestamp: str | None = None) -> str:
    if not timestamp:
        return datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")

    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    return dt.astimezone(WIB).strftime("%Y-%m-%d %H:%M:%S")


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

        TIMESTAMP = get_timestamp(custom_timestamp)

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
