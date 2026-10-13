from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.document import Document
from shared.util import serialize

from ..schemas.document import DocumentsRow


class DocumentRepository:
    def get_documents(self, participant_id: str) -> list[DocumentsRow]:

        query = (
            select(
                Document.id,
                Document.owner_id,
                Document.owner_type,
                Document.document_type,
                Document.s3_key,
                Document.content_type,
                Document.original_filename,
                func.coalesce(Document.updated_at, Document.created_at).label(
                    "last_modified_at"
                ),
            )
            .select_from(Document)
            .where(
                (Document.is_deleted == False)
                & (Document.owner_id == participant_id)
                & (Document.owner_type == "participant")
            )
        )

        documents = serialize(
            db.session.execute(query).all(),
            DocumentsRow,
        )

        return documents
