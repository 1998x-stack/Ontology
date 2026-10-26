from auto_ontology.extractor import extract_candidates
from auto_ontology.models import ParsedBlock


def block(text: str) -> ParsedBlock:
    return ParsedBlock(1, 0, "4.2.1", text, (10, 20, 200, 100))


def test_narrative_text_not_promoted():
    assert extract_candidates([block("The fragrance system could send updates.")]) == []


def test_conservative_normative_extraction():
    data = extract_candidates([
        block("HU SHALL send FragranceRequest=1."),
        block("HVAC_ECU MUST emit FragranceStatus=1 within 1000 ms.")
    ])
    assert len(data) == 2
    assert data[0].actor_mention == "HU"
    assert data[0].signal_mentions == ["FragranceRequest"]
    assert data[1].timing_value == 1000.0
    assert data[1].timing_unit == "ms"
    assert data[1].timing_operator == "<="
    assert "timing_reference_event_unresolved" in data[1].flags


def test_negation_and_condition_are_never_silently_approved():
    found = extract_candidates([block("If HVAC=OFF, HU SHALL not send FragranceRequest=1.")])
    assert len(found) == 1
    assert "negation_or_exception_scope_unparsed" in found[0].flags
    assert "compound_condition_scope_unparsed" in found[0].flags


def test_chinese_normative_candidate():
    found = extract_candidates([block("空调 ECU 应在 500 毫秒内反馈 FragranceStatus=1。")])
    assert len(found) == 1
    assert found[0].timing_value == 500
    assert found[0].timing_unit == "ms"
    assert found[0].signal_mentions == ["FragranceStatus"]
