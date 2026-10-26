"""HTTP API for candidate-only ingestion. Single shared key: prototype, not multi-tenant ACL."""
from __future__ import annotations

import os
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, Response

from .db import Database
from .models import CandidateView, DocumentView, IngestionResponse, SourceAnchorView
from .parser import InvalidDocument, MAX_BYTES
from .service import IngestionService, NotFound, RevisionConflict
from .validation import load_contract


def create_app(*, database_url: str | None = None, api_key: str | None = None) -> FastAPI:
    db = Database(database_url)
    db.create_schema()
    service = IngestionService(db)
    expected_key = api_key if api_key is not None else os.getenv("ONTOLOGY_API_KEY", "")

    app = FastAPI(title="Automotive Ontology - Candidate Ingestion", version="1.0.0a0")
    app.state.db = db

    def authenticated(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None) -> None:
        if not expected_key:
            raise HTTPException(status_code=503, detail="API authentication is not configured")
        if not secrets.compare_digest(x_api_key or "", expected_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

    def guard_error(exc: Exception) -> HTTPException:
        if isinstance(exc, NotFound):
            return HTTPException(status_code=404, detail=str(exc))
        if isinstance(exc, RevisionConflict):
            return HTTPException(status_code=409, detail=str(exc))
        if isinstance(exc, (InvalidDocument, ValueError)):
            return HTTPException(status_code=422, detail=str(exc))
        return HTTPException(status_code=500, detail="Internal error")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "candidate-only"}

    @app.get("/api/v1/schema", dependencies=[Depends(authenticated)])
    def schema() -> dict:
        return load_contract()

    @app.post("/api/v1/documents", response_model=IngestionResponse, status_code=201, dependencies=[Depends(authenticated)])
    async def upload(
        file: Annotated[UploadFile, File()],
        project_id: Annotated[str, Form(min_length=1)],
        document_code: Annotated[str, Form(min_length=1)],
        revision: Annotated[str, Form(min_length=1)],
    ) -> IngestionResponse:
        if file.filename is None or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=422, detail="Filename must end with .pdf")
        content = await file.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="PDF exceeds maximum upload size")
        try:
            return service.ingest(
                content, project_id=project_id, document_code=document_code,
                revision=revision, filename=file.filename
            )
        except (InvalidDocument, RevisionConflict, ValueError) as exc:
            raise guard_error(exc) from exc

    @app.get("/api/v1/documents", response_model=list[DocumentView], dependencies=[Depends(authenticated)])
    def list_documents(project_id: str) -> list[DocumentView]:
        return service.list_documents(project_id)

    @app.get("/api/v1/documents/{document_id}", response_model=DocumentView, dependencies=[Depends(authenticated)])
    def document(document_id: str) -> DocumentView:
        try:
            return service.get_document(document_id)
        except NotFound as exc:
            raise guard_error(exc) from exc

    @app.get("/api/v1/documents/{document_id}/source", dependencies=[Depends(authenticated)])
    def source_pdf(document_id: str) -> Response:
        try:
            contents = service.get_source_pdf(document_id)
        except NotFound as exc:
            raise guard_error(exc) from exc
        return Response(content=contents, media_type="application/pdf", headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": 'inline; filename="source.pdf"'
        })

    @app.get("/api/v1/documents/{document_id}/candidates", response_model=list[CandidateView], dependencies=[Depends(authenticated)])
    def candidates(document_id: str) -> list[CandidateView]:
        try:
            return service.list_candidates(document_id)
        except NotFound as exc:
            raise guard_error(exc) from exc

    @app.get("/api/v1/anchors/{anchor_id}", response_model=SourceAnchorView, dependencies=[Depends(authenticated)])
    def anchor(anchor_id: str) -> SourceAnchorView:
        try:
            return service.get_anchor(anchor_id)
        except NotFound as exc:
            raise guard_error(exc) from exc

    return app


app = create_app()
