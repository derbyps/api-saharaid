from uuid import UUID

from sqlalchemy import delete, select

from shared.configs.db import db
from shared.models.document import Document, DocumentDeletion
from shared.models.participant import Participant

from ..schemas.document import DocumentDeletionRow, DocumentMetadataRow, DocumentRow


class DocumentRepository:
    def pending_for_owner(self, owner_id: UUID, remove_ids: set[UUID]) -> list[DocumentDeletionRow]:
        if not remove_ids:
            return []
        pending = db.session.scalars(
            select(DocumentDeletion).where(
                DocumentDeletion.participant_id == owner_id,
                DocumentDeletion.document_id.in_(remove_ids),
            )
        ).all()
        return [
            DocumentDeletionRow(document_id=str(item.document_id), s3_key=item.s3_key)
            for item in pending
        ]

    def list_for_owner(self, owner_id: UUID) -> list[DocumentRow]:
        documents = db.session.scalars(
            select(Document).where(Document.participant_id == owner_id)
        ).all()
        return [
            DocumentRow(id=str(item.id), document_type=item.document_type, s3_key=item.s3_key)
            for item in documents
        ]

    def list_metadata_for_owner(self, owner_id: UUID) -> list[DocumentMetadataRow]:
        documents = db.session.scalars(
            select(Document).where(Document.participant_id == owner_id)
        ).all()
        return [
            DocumentMetadataRow(
                id=str(item.id),
                document_type=item.document_type,
                original_filename=item.original_filename,
                content_type=item.content_type,
                file_size=item.file_size,
                last_modified_at=item.last_modified_at.isoformat(),
                uploaded_at=item.uploaded_at.isoformat(),
            )
            for item in documents
        ]

    def get_active_document(self, document_id: UUID) -> DocumentRow | None:
        item = db.session.scalar(
            select(Document).join(Participant, Participant.id == Document.participant_id).where(
                Document.id == document_id, Participant.is_deleted.is_(False)
            )
        )
        return DocumentRow(id=str(item.id), document_type=item.document_type, s3_key=item.s3_key) if item else None

    def save(
        self,
        owner_id: UUID,
        actor_id: UUID,
        additions: list[dict],
        removed: list[DocumentRow],
    ) -> list[DocumentMetadataRow]:
        if removed:
            db.session.add_all(
                DocumentDeletion(
                    document_id=UUID(item["id"]), participant_id=owner_id, s3_key=item["s3_key"]
                )
                for item in removed
            )
            db.session.flush()
            db.session.execute(
                delete(Document).where(
                    Document.participant_id == owner_id,
                    Document.id.in_({UUID(item["id"]) for item in removed}),
                )
            )
            db.session.flush()
        db.session.add_all(
            Document(participant_id=owner_id, created_by=actor_id, **item)
            for item in additions
        )
        db.session.flush()
        return self.list_metadata_for_owner(owner_id)

    def clear_pending(self, document_id: UUID) -> None:
        db.session.execute(
            delete(DocumentDeletion).where(DocumentDeletion.document_id == document_id)
        )
