"""Boundary models for document ingestion; all requirements are candidates."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from pydantic import BaseModel, Field


@dataclass(frozen=True)
class ParsedBlock:
    page_no: int
    block_index: int
    section_path: str | None
    text: str
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class ExtractedCandidate:
    anchor_index: int
    source_text: str
    actor_mention: str | None
    signal_mentions: list[str] = field(default_factory=list)
    timing_value: float | None = None
    timing_unit: str | None = None
    timing_operator: str | None = None
    flags: list[str] = field(default_factory=list)


class TimingConstraint(BaseModel):
    operator: Literal["<", "<=", "=", ">", ">="]
    value: float = Field(ge=0)
    unit: Literal["ms", "s"]


class CandidateView(BaseModel):
    id: str
    document_id: str
    source_anchor_id: str
    source_text: str
    actor_mention: str | None
    signal_mentions: list[str]
    timing: TimingConstraint | None
    review_status: Literal["candidate"] = "candidate"
    requires_review: bool = True
    quality_flags: list[str]


class SourceAnchorView(BaseModel):
    id: str
    document_id: str
    page_no: int
    block_index: int
    section_path: str | None
    source_text: str
    bbox: list[float]
    text_sha256: str


class IngestionResponse(BaseModel):
    id: str
    project_id: str
    document_code: str
    revision: str
    sha256: str
    pages: int
    block_count: int
    candidate_count: int
    reused: bool


class DocumentView(IngestionResponse):
    filename: str


class ErrorResponse(BaseModel):
    detail: str
