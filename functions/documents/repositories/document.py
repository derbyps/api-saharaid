from sqlalchemy import delete, select

from shared.configs.db import db
from shared.models.document import Document


class DocumentRepository:
    def get_active_by_types(
        self, owner_id: str, owner_type: str, document_types: list[str]
    ) -> list[Document]:
        return list(
            db.session.scalars(
                select(Document).where(
                    (Document.owner_id == owner_id)
                    & (Document.owner_type == owner_type)
                    & (Document.is_deleted == False)
                    & (Document.document_type.in_(document_types))
                )
            ).all()
        )

    def remove(self, owner_id: str, owner_type: str, ids: list[str]) -> None:
        if not ids:
            return

        db.session.execute(
            delete(Document).where(
                Document.id.in_(ids)
                & (Document.owner_id == owner_id)
                & (Document.owner_type == owner_type)
            )
        )
