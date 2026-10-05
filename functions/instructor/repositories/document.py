from sqlalchemy import select

from shared.configs.db import db
from shared.models.document import Document
from shared.util import serialize

from ..schemas.document import DocumentsRow


class DocumentRepository:
    def get_documents(self, instructor_id: str) -> list[DocumentsRow]:

        query = (
            select(
                Document.id,
                Document.owner_id,
                Document.owner_type,
                Document.document_type,
                Document.s3_key,
                Document.content_type,
            )
            .select_from(Document)
            .where(
                (Document.is_deleted == False)
                & (Document.owner_id == instructor_id)
                & (Document.owner_type == "instructor")
            )
        )

        documents = serialize(
            db.session.execute(query).all(),
            DocumentsRow,
        )

        return documents
