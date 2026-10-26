"""Authoritative Stage 1 document/candidate store; no publishing API."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


def new_id() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    __tablename__ = "document_revision"
    __table_args__ = (UniqueConstraint("project_id", "document_code", "revision", name="uq_document_revision"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    document_code: Mapped[str] = mapped_column(String(120), nullable=False)
    revision: Mapped[str] = mapped_column(String(64), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    raw_pdf: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    block_count: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    anchors: Mapped[list["AnchorRecord"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    candidates: Mapped[list["CandidateRecord"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class AnchorRecord(Base):
    __tablename__ = "source_anchor"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_revision.id"), nullable=False, index=True)
    page_no: Mapped[int] = mapped_column(Integer, nullable=False)
    block_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_path: Mapped[str | None] = mapped_column(String(120))
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    bbox: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    document: Mapped[DocumentRecord] = relationship(back_populates="anchors")


class CandidateRecord(Base):
    __tablename__ = "requirement_candidate"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_revision.id"), nullable=False, index=True)
    anchor_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_anchor.id"), nullable=False, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    actor_mention: Mapped[str | None] = mapped_column(String(128))
    signal_mentions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    timing_value: Mapped[float | None] = mapped_column()
    timing_unit: Mapped[str | None] = mapped_column(String(8))
    timing_operator: Mapped[str | None] = mapped_column(String(8))
    quality_flags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    review_status: Mapped[str] = mapped_column(String(24), default="candidate", nullable=False)
    document: Mapped[DocumentRecord] = relationship(back_populates="candidates")
    anchor: Mapped[AnchorRecord] = relationship()


class ExtractionRun(Base):
    __tablename__ = "extraction_run"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_revision.id"), nullable=False, index=True)
    extractor: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False)


class Database:
    def __init__(self, url: str | None = None):
        url = url or os.getenv("DATABASE_URL", "sqlite:///./ontology.db")
        args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        kwargs = {"connect_args": args}
        if url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool
        self.engine = create_engine(url, **kwargs)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()
