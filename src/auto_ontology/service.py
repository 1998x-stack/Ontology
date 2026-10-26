"""Stage 1 idempotent ingestion with source anchors and candidate-only extraction."""
from __future__ import annotations

from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import AnchorRecord, CandidateRecord, Database, DocumentRecord, ExtractionRun
from .extractor import extract_candidates
from .models import CandidateView, DocumentView, IngestionResponse, SourceAnchorView, TimingConstraint
from .parser import parse_pdf
from .validation import load_contract, validate_candidate


class RevisionConflict(ValueError):
    pass


class NotFound(LookupError):
    pass


class IngestionService:
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _summary(doc: DocumentRecord, reused: bool) -> IngestionResponse:
        return IngestionResponse(
            id=doc.id, project_id=doc.project_id, document_code=doc.document_code,
            revision=doc.revision, sha256=doc.sha256, pages=doc.pages,
            block_count=doc.block_count, candidate_count=doc.candidate_count, reused=reused,
        )

    def ingest(self, pdf: bytes, *, project_id: str, document_code: str, revision: str, filename: str) -> IngestionResponse:
        if not (project_id.strip() and document_code.strip() and revision.strip()):
            raise ValueError("project_id, document_code and revision cannot be empty")
        digest = sha256(pdf).hexdigest()
        with self.db.sessions() as session:
            existing = session.scalar(select(DocumentRecord).where(
                DocumentRecord.project_id == project_id,
                DocumentRecord.document_code == document_code,
                DocumentRecord.revision == revision,
            ))
            if existing:
                if existing.sha256 != digest:
                    raise RevisionConflict("A different file already exists for this project/document/revision")
                return self._summary(existing, reused=True)

        pages, blocks = parse_pdf(pdf)
        extracted = extract_candidates(blocks)
        contract = load_contract()
        for candidate in extracted:
            validate_candidate(candidate, blocks[candidate.anchor_index])
        doc = DocumentRecord(
            project_id=project_id, document_code=document_code, revision=revision,
            filename=filename[:256], raw_pdf=pdf, sha256=digest,
            pages=pages, block_count=len(blocks), candidate_count=len(extracted)
        )
        try:
            with self.db.sessions.begin() as session:
                session.add(doc)
                session.flush()
                anchors: list[AnchorRecord] = []
                for block in blocks:
                    anchor = AnchorRecord(
                        document_id=doc.id, page_no=block.page_no, block_index=block.block_index,
                        section_path=block.section_path, source_text=block.text,
                        text_sha256=sha256(block.text.encode("utf-8")).hexdigest(), bbox=list(block.bbox)
                    )
                    session.add(anchor)
                    anchors.append(anchor)
                session.flush()
                for item in extracted:
                    anchor = anchors[item.anchor_index]
                    if item.source_text not in anchor.source_text:
                        raise AssertionError("Extracted candidate has no verbatim source anchor")
                    session.add(CandidateRecord(
                        document_id=doc.id, anchor_id=anchor.id, source_text=item.source_text,
                        actor_mention=item.actor_mention, signal_mentions=item.signal_mentions,
                        timing_value=item.timing_value, timing_unit=item.timing_unit,
                        timing_operator=item.timing_operator, quality_flags=item.flags,
                        review_status="candidate"
                    ))
                session.add(ExtractionRun(
                    document_id=doc.id, extractor="deterministic-regex-v1",
                    schema_version=contract["schema_version"], status="completed",
                    candidate_count=len(extracted)
                ))
        except IntegrityError:
            # A concurrent upload might have inserted the same revision.
            with self.db.sessions() as session:
                existing = session.scalar(select(DocumentRecord).where(
                    DocumentRecord.project_id == project_id,
                    DocumentRecord.document_code == document_code,
                    DocumentRecord.revision == revision,
                ))
                if existing and existing.sha256 == digest:
                    return self._summary(existing, reused=True)
            raise RevisionConflict("Revision conflict during concurrent upload")
        return self._summary(doc, reused=False)

    def get_source_pdf(self, document_id: str) -> bytes:
        """Return original immutable PDF bytes under API authorization."""
        with self.db.sessions() as session:
            d = session.get(DocumentRecord, document_id)
            if d is None:
                raise NotFound("Document not found")
            return d.raw_pdf

    def get_document(self, document_id: str) -> DocumentView:
        with self.db.sessions() as session:
            d = session.get(DocumentRecord, document_id)
            if d is None:
                raise NotFound("Document not found")
            return DocumentView(**self._summary(d, reused=False).model_dump(), filename=d.filename)

    def list_documents(self, project_id: str) -> list[DocumentView]:
        with self.db.sessions() as session:
            records = session.scalars(select(DocumentRecord).where(DocumentRecord.project_id == project_id).order_by(DocumentRecord.document_code, DocumentRecord.revision)).all()
            return [DocumentView(**self._summary(d, reused=False).model_dump(), filename=d.filename) for d in records]

    def list_candidates(self, document_id: str) -> list[CandidateView]:
        self.get_document(document_id)
        with self.db.sessions() as session:
            rows = session.scalars(select(CandidateRecord).where(CandidateRecord.document_id == document_id).order_by(CandidateRecord.id)).all()
            return [
                CandidateView(
                    id=c.id, document_id=c.document_id, source_anchor_id=c.anchor_id,
                    source_text=c.source_text, actor_mention=c.actor_mention,
                    signal_mentions=c.signal_mentions,
                    timing=TimingConstraint(operator=c.timing_operator, value=c.timing_value, unit=c.timing_unit)
                        if c.timing_operator and c.timing_value is not None and c.timing_unit else None,
                    quality_flags=c.quality_flags,
                ) for c in rows
            ]

    def get_anchor(self, anchor_id: str) -> SourceAnchorView:
        with self.db.sessions() as session:
            a = session.get(AnchorRecord, anchor_id)
            if a is None:
                raise NotFound("Anchor not found")
            return SourceAnchorView(
                id=a.id, document_id=a.document_id, page_no=a.page_no,
                block_index=a.block_index, section_path=a.section_path,
                source_text=a.source_text, bbox=a.bbox, text_sha256=a.text_sha256
            )
