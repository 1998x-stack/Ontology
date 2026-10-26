from __future__ import annotations

import fitz
import pytest


@pytest.fixture
def make_pdf():
    def build(*pages: list[str]) -> bytes:
        doc = fitz.open()
        for rows in pages:
            page = doc.new_page()
            for i, line in enumerate(rows):
                page.insert_text((60, 80 + 28 * i), line, fontsize=11)
        data = doc.tobytes()
        doc.close()
        return data
    return build


@pytest.fixture
def sample_pdf(make_pdf):
    return make_pdf(
        [
            "4.2.1 Fragrance Control",
            "HU SHALL send FragranceRequest=1.",
            "HVAC_ECU MUST emit FragranceStatus=1 within 1000 ms."
        ],
        ["Informative note: this section is an example only."]
    )
