from __future__ import annotations

from dataclasses import replace

import pytest

from auto_ontology.models import ExtractedCandidate, ParsedBlock
from auto_ontology.validation import CandidateValidationError, load_contract, validate_candidate


@pytest.fixture
def block():
    return ParsedBlock(
        page_no=42, block_index=1, section_path="4.2.1",
        text="HU SHALL send FragranceRequest=1 within 1000 ms.",
        bbox=(50.0, 90.0, 500.0, 115.0),
    )


@pytest.fixture
def candidate():
    return ExtractedCandidate(
        anchor_index=0,
        source_text="HU SHALL send FragranceRequest=1 within 1000 ms.",
        actor_mention="HU",
        signal_mentions=["FragranceRequest"],
        timing_value=1000.0, timing_operator="<=", timing_unit="ms",
        flags=["deterministic_baseline_unverified", "timing_reference_event_unresolved"],
    )


def test_contract_is_candidate_only():
    contract = load_contract()
    assert contract["schema_version"] == "0.1.0"
    assert contract["security"]["candidate_only"] is True
    assert contract["security"]["default_publish_allowed"] is False


def test_grounded_candidate_allowed(candidate, block):
    validate_candidate(candidate, block)


@pytest.mark.parametrize("changed", [
    {"source_text": "Fabricated statement not present in PDF"},
    {"timing_value": -1.0},
    {"timing_operator": None},
    {"timing_unit": "minutes"},
    {"signal_mentions": ["Fake; DROP TABLE"]},
    {"flags": []},
])
def test_untrusted_candidate_rejected(candidate, block, changed):
    with pytest.raises(CandidateValidationError):
        validate_candidate(replace(candidate, **changed), block)


def test_missing_evidence_bbox_rejected(candidate, block):
    invalid_block = replace(block, bbox=(1.0, 3.0, 0.0, 2.0))
    with pytest.raises(CandidateValidationError):
        validate_candidate(candidate, invalid_block)
