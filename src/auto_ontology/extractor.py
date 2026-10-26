"""Conservative, deterministic candidate extraction; not a semantic parser."""
from __future__ import annotations

import re

from .models import ExtractedCandidate, ParsedBlock

# Avoid confusing arbitrary prose with reviewed engineering requirements.
NORMATIVE = re.compile(r"\b(?:shall|must)\b|必须|应当|应在|应发送|应反馈|すること", re.I)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|(?<=[。！？])")
SIGNAL_MENTION = re.compile(r"\b([A-Za-z][A-Za-z0-9_]{2,})\s*={1,2}\s*([A-Za-z0-9_]+)")
TIMING_EN = re.compile(r"\bwithin\s+(\d+(?:\.\d+)?)\s*(ms|milliseconds?|s|seconds?)\b", re.I)
TIMING_ZH = re.compile(r"(\d+(?:\.\d+)?)\s*(ms|毫秒|秒)\s*内")
ACTOR = re.compile(r"\b(HU|[A-Za-z][A-Za-z0-9_]*(?:_ECU| ECU))\s+(?:shall|must)\b", re.I)
AMBIGUOUS = re.compile(r"\b(?:unless|except|not|only if|until|before|after)\b|除非|不得|不应|仅当|以外", re.I)
CONDITION = re.compile(r"\b(?:if|when|while|and|or)\b|如果|当|且|或者|以及|または", re.I)


def extract_candidates(blocks: list[ParsedBlock]) -> list[ExtractedCandidate]:
    found: list[ExtractedCandidate] = []
    for index, block in enumerate(blocks):
        for sentence in SENTENCE_SPLIT.split(block.text):
            sentence = sentence.strip()
            if not sentence or not NORMATIVE.search(sentence):
                continue
            matches = SIGNAL_MENTION.findall(sentence)
            mentions = list(dict.fromkeys(name for name, _ in matches))
            flags = ["deterministic_baseline_unverified"]
            if AMBIGUOUS.search(sentence):
                flags.append("negation_or_exception_scope_unparsed")
            if CONDITION.search(sentence):
                flags.append("compound_condition_scope_unparsed")
            if len(matches) > 1:
                flags.append("multiple_signal_values_unresolved")
            actor = ACTOR.search(sentence)
            timing = TIMING_EN.search(sentence) or TIMING_ZH.search(sentence)
            value, unit, operator = None, None, None
            if timing:
                value = float(timing.group(1))
                raw_unit = timing.group(2).lower()
                unit = "ms" if raw_unit.startswith("m") or raw_unit == "毫秒" else "s"
                operator = "<="
                flags.append("timing_reference_event_unresolved")
            # No guessed canonical IDs, actor, signal direction or event semantics.
            found.append(ExtractedCandidate(
                anchor_index=index,
                source_text=sentence,
                actor_mention=actor.group(1) if actor else None,
                signal_mentions=mentions,
                timing_value=value,
                timing_unit=unit,
                timing_operator=operator,
                flags=flags,
            ))
    return found
