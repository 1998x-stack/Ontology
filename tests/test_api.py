from fastapi.testclient import TestClient

from auto_ontology.api import create_app
from auto_ontology.parser import MAX_BYTES


def test_full_api_lifecycle(tmp_path, sample_pdf):
    app = create_app(database_url="sqlite:///" + str(tmp_path / "web.db"), api_key="secret")
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/api/v1/documents", params={"project_id": "A"}).status_code == 401
        headers = {"X-API-Key": "secret"}
        schema = client.get("/api/v1/schema", headers=headers)
        assert schema.status_code == 200
        assert schema.json()["security"]["candidate_only"] is True

        data = {"project_id": "P", "document_code": "SPEC-573", "revision": "2.1"}
        file = {"file": ("spec.pdf", sample_pdf, "application/pdf")}
        response = client.post("/api/v1/documents", data=data, files=file, headers=headers)
        assert response.status_code == 201, response.text
        uploaded = response.json()
        assert uploaded["candidate_count"] == 2
        doc_id = uploaded["id"]
        doc = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        assert doc.status_code == 200
        assert doc.json()["filename"] == "spec.pdf"

        candidates = client.get(f"/api/v1/documents/{doc_id}/candidates", headers=headers)
        assert candidates.status_code == 200
        assert len(candidates.json()) == 2
        anchor_id = candidates.json()[0]["source_anchor_id"]
        anchor = client.get(f"/api/v1/anchors/{anchor_id}", headers=headers)
        assert anchor.status_code == 200
        assert anchor.json()["page_no"] == 1

        repeat = client.post("/api/v1/documents", data=data, files=file, headers=headers)
        assert repeat.status_code == 201
        assert repeat.json()["reused"] is True

        listing = client.get("/api/v1/documents", params={"project_id": "P"}, headers=headers)
        assert len(listing.json()) == 1
        unknown = client.get("/api/v1/documents/missing", headers=headers)
        assert unknown.status_code == 404
    app.state.db.close()


def test_fail_closed_without_key(tmp_path):
    app = create_app(database_url="sqlite:///" + str(tmp_path / "nokey.db"), api_key="")
    with TestClient(app) as client:
        assert client.get("/api/v1/schema").status_code == 503
    app.state.db.close()


def test_upload_validation(tmp_path, sample_pdf):
    app = create_app(database_url="sqlite:///" + str(tmp_path / "invalid.db"), api_key="secret")
    with TestClient(app) as client:
        data = {"project_id": "P", "document_code": "X", "revision": "1"}
        headers = {"X-API-Key": "secret"}
        assert client.post("/api/v1/documents", headers=headers, data=data, files={"file": ("bad.txt", sample_pdf)}).status_code == 422
        assert client.post("/api/v1/documents", headers=headers, data=data, files={"file": ("bad.pdf", b"not pdf")}).status_code == 422
        assert client.post("/api/v1/documents", headers=headers, data=data, files={"file": ("huge.pdf", b"%PDF-" + b"x" * MAX_BYTES)}).status_code == 413
    app.state.db.close()
