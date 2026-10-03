from sqlalchemy import delete

from shared.configs.db import db
from shared.models.document import Document


class DocumentRepository:
    def remove(self, ids: list[str]) -> None:
        db.session.execute(delete(Document).where(Document.id.in_(ids)))
