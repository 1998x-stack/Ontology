import pytest

from auto_ontology.db import Database
from auto_ontology.parser import InvalidDocument, parse_pdf
from auto_ontology.service import IngestionService, NotFound, RevisionConflict


def setup_service(tmp_path):
    db = Database("sqlite:///" + str(tmp_path / "test.db"))
    db.create_schema()
    return db, IngestionService(db)


def test_document_ingestion_evidence_and_idempotency(tmp_path, sample_pdf):
    db, service = setup_service(tmp_path)
    first = service.ingest(
        sample_pdf, project_id="TEST", document_code="SPEC-573",
        revision="2.1", filename="spec.pdf"
    )
    assert first.reused is False
    assert first.pages == 2
    assert first.candidate_count == 2
    assert first.block_count >= 3
    candidates = service.list_candidates(first.id)
    assert len(candidates) == 2
    assert all(c.review_status == "candidate" and c.requires_review for c in candidates)
    assert all("deterministic_baseline_unverified" in c.quality_flags for c in candidates)

    anchors = [service.get_anchor(c.source_anchor_id) for c in candidates]
    assert all(a.page_no == 1 for a in anchors)
    assert all(len(a.bbox) == 4 and a.source_text for a in anchors)
    assert all(c.source_text in a.source_text for c, a in zip(candidates, anchors))
    assert all(len(a.text_sha256) == 64 for a in anchors)

    duplicate = service.ingest(
        sample_pdf, project_id="TEST", document_code="SPEC-573",
        revision="2.1", filename="uploaded-again.pdf"
    )
    assert duplicate.id == first.id
    assert duplicate.reused is True
    assert len(service.list_candidates(first.id)) == 2
    assert len(service.list_documents("TEST")) == 1
    db.close()


def test_revision_content_conflict_and_project_isolation(tmp_path, make_pdf, sample_pdf):
    db, service = setup_service(tmp_path)
    first = service.ingest(sample_pdf, project_id="P1", document_code="S", revision="A", filename="a.pdf")
    with pytest.raises(RevisionConflict):
        service.ingest(make_pdf(["A different SHA SHALL be rejected."]), project_id="P1", document_code="S", revision="A", filename="b.pdf")
    second = service.ingest(sample_pdf, project_id="P2", document_code="S", revision="A", filename="a.pdf")
    assert second.id != first.id
    assert service.list_documents("P1")[0].id == first.id
    assert service.list_documents("P2")[0].id == second.id
    db.close()


def test_reopen_database_and_missing_document(tmp_path, sample_pdf):
    db, service = setup_service(tmp_path)
    record = service.ingest(sample_pdf, project_id="P", document_code="S", revision="1", filename="s.pdf")
    db.close()
    db2, service2 = setup_service(tmp_path)
    assert service2.get_document(record.id).sha256 == record.sha256
    assert len(service2.list_candidates(record.id)) == 2
    with pytest.raises(NotFound):
        service2.get_anchor("00000000-0000-0000-0000-000000000000")
    db2.close()


def test_invalid_pdf(tmp_path):
    db, service = setup_service(tmp_path)
    with pytest.raises(InvalidDocument):
        service.ingest(b"not a PDF", project_id="P", document_code="X", revision="1", filename="x.pdf")
    assert service.list_documents("P") == []
    db.close()


def test_max_page_count(make_pdf):
    too_long = make_pdf(*([["page"]]*101))
    with pytest.raises(InvalidDocument, match="maximum page count"):
        parse_pdf(too_long)
