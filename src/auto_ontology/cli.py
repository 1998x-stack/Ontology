"""CLI for local ingestion and candidate inspection."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .db import Database
from .service import IngestionService


def main() -> None:
    parser = argparse.ArgumentParser(prog="ontology", description="Automotive ontology candidate ingestion")
    parser.add_argument("--db", default=os.getenv("DATABASE_URL", "sqlite:///./ontology.db"))
    command = parser.add_subparsers(dest="command", required=True)
    ingest = command.add_parser("ingest", help="Ingest a PDF into candidate-only store")
    ingest.add_argument("pdf", type=Path)
    ingest.add_argument("--project", required=True)
    ingest.add_argument("--code", required=True)
    ingest.add_argument("--revision", required=True)
    show = command.add_parser("list", help="List revisions in a project")
    show.add_argument("--project", required=True)
    command.add_parser("serve", help="Start FastAPI service (requires ONTOLOGY_API_KEY)")
    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn
        if not os.getenv("ONTOLOGY_API_KEY"):
            parser.error("ONTOLOGY_API_KEY is required for the HTTP service")
        os.environ["DATABASE_URL"] = args.db
        uvicorn.run("auto_ontology.api:app", host="127.0.0.1", port=8000, reload=False)
        return

    db = Database(args.db)
    db.create_schema()
    service = IngestionService(db)
    if args.command == "ingest":
        result = service.ingest(args.pdf.read_bytes(), project_id=args.project, document_code=args.code, revision=args.revision, filename=args.pdf.name)
        print(result.model_dump_json(indent=2))
    elif args.command == "list":
        print(json.dumps([x.model_dump() for x in service.list_documents(args.project)], indent=2, ensure_ascii=False))
    db.close()


if __name__ == "__main__":
    main()
