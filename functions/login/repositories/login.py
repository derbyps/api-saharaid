from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.user import User

from ..schemas.login import LoginUserRow


class LoginRepository:
    def get_user_by_email(self, email: str) -> LoginUserRow | None:
        user = db.session.execute(
            select(User.id, User.name, User.email).where(
                func.lower(func.trim(User.email)) == email.lower()
            )
        ).one_or_none()
        if user is None:
            return None
        return {"id": str(user.id), "name": user.name, "email": user.email}
