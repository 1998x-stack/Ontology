"""Real PostgreSQL integration path on CI, skipped when no server is configured."""
from __future__ import annotations

import os
from uuid import uuid4

import pytest

from auto_ontology.db import Database
from auto_ontology.service import IngestionService, RevisionConflict

POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")

@pytest.mark.skipif(not POSTGRES_URL, reason="TEST_POSTGRES_URL not configured")
def test_postgres_persistence_and_unique_revision(sample_pdf, make_pdf):
    db = Database(POSTGRES_URL)
    try:
        db.create_schema()
        svc = IngestionService(db)
        project = "CI-" + uuid4().hex
        result = svc.ingest(sample_pdf, project_id=project, document_code="SPEC-573", revision="2.1", filename="sample.pdf")
        assert result.candidate_count == 2
        assert svc.get_source_pdf(result.id) == sample_pdf
        anchor = svc.get_anchor(svc.list_candidates(result.id)[0].source_anchor_id)
        assert anchor.page_no == 1
        assert anchor.bbox[2] > anchor.bbox[0]
        again = svc.ingest(sample_pdf, project_id=project, document_code="SPEC-573", revision="2.1", filename="sample.pdf")
        assert again.id == result.id
        assert again.reused is True
        with pytest.raises(RevisionConflict):
            svc.ingest(make_pdf(["HU SHALL send NewSignal=1."]), project_id=project, document_code="SPEC-573", revision="2.1", filename="other.pdf")
    finally:
        db.close()
