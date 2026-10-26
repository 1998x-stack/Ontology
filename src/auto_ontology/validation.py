"""Validate every candidate against the Stage 1 immutable ontology contract.

This is structural/grounding validation only; it cannot establish semantic truth.
"""
from __future__ import annotations

import re
from functools import lru_cache
from importlib.resources import files

import yaml
from pydantic import ValidationError

from .models import ExtractedCandidate, ParsedBlock, TimingConstraint


class CandidateValidationError(ValueError):
    """Candidate cannot be safely stored with the selected ontology contract."""


@lru_cache(maxsize=1)
def load_contract() -> dict:
    raw = files("auto_ontology").joinpath("schemas/automotive.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict) or not isinstance(data.get("schema_version"), str):
        raise CandidateValidationError("Invalid ontology schema: missing version")
    security = data.get("security", {})
    if security.get("candidate_only") is not True or security.get("default_publish_allowed") is not False:
        raise CandidateValidationError("Stage 1 ontology contract must be candidate-only")
    if not isinstance(data.get("classes"), dict) or "AtomicRequirementCandidate" not in data["classes"]:
        raise CandidateValidationError("Invalid ontology schema: missing candidate class")
    return data


def validate_candidate(candidate: ExtractedCandidate, block: ParsedBlock) -> None:
    if not candidate.source_text.strip() or candidate.source_text not in block.text:
        raise CandidateValidationError("Candidate text is not verbatim grounded in its source block")
    if block.page_no <= 0 or len(block.bbox) != 4 or block.bbox[2] <= block.bbox[0] or block.bbox[3] <= block.bbox[1]:
        raise CandidateValidationError("Invalid source location or PDF bounding box")
    if "deterministic_baseline_unverified" not in candidate.flags:
        raise CandidateValidationError("Candidates must explicitly disclose extraction uncertainty")

    for mention in candidate.signal_mentions:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,}", mention):
            raise CandidateValidationError("Invalid signal mention; canonical identities require master data")

    pieces = (candidate.timing_operator, candidate.timing_value, candidate.timing_unit)
    if any(v is not None for v in pieces):
        if not all(v is not None for v in pieces):
            raise CandidateValidationError("Incomplete timing constraint")
        try:
            TimingConstraint(operator=candidate.timing_operator, value=candidate.timing_value, unit=candidate.timing_unit)
        except ValidationError as exc:
            raise CandidateValidationError("Invalid timing constraint") from exc
