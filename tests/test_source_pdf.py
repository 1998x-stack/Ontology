from fastapi.testclient import TestClient

from auto_ontology.api import create_app
from auto_ontology.db import Database
from auto_ontology.parser import parse_pdf
from auto_ontology.service import IngestionService


def test_original_pdf_retrieval_requires_key(tmp_path, sample_pdf):
    app = create_app(database_url="sqlite:///" + str(tmp_path / "source.db"), api_key="secret")
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents",
            headers={"X-API-Key": "secret"},
            data={"project_id": "P", "document_code": "SPEC-573", "revision": "2.1"},
            files={"file": ("example.pdf", sample_pdf, "application/pdf")},
        )
        document_id = response.json()["id"]
        url = f"/api/v1/documents/{document_id}/source"
        assert client.get(url).status_code == 401
        raw = client.get(url, headers={"X-API-Key": "secret"})
        assert raw.status_code == 200
        assert raw.content == sample_pdf
        assert raw.headers["cache-control"] == "no-store"
        assert raw.headers["content-type"].startswith("application/pdf")
        assert client.get("/api/v1/documents/missing/source", headers={"X-API-Key": "secret"}).status_code == 404
    app.state.db.close()


def test_no_normative_sentences_keeps_zero_candidates(tmp_path, make_pdf):
    db = Database("sqlite:///" + str(tmp_path / "empty.db"))
    db.create_schema()
    try:
        svc = IngestionService(db)
        pdf = make_pdf(["Informative note about the HVAC system."])
        result = svc.ingest(pdf, project_id="P", document_code="INFO", revision="A", filename="info.pdf")
        assert result.candidate_count == 0
        assert svc.list_candidates(result.id) == []
        assert len(svc.list_documents("P")) == 1
    finally:
        db.close()
