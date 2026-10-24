import pymupdf

from app.extract import extract_pdf
from app.pdfout import redact_pdf
from app.pipeline import T1Result, run_pipeline


def test_redacted_pdf_has_the_values_removed_not_just_covered(tenancy_pdf):
    doc = extract_pdf(tenancy_pdf, "lease.pdf")

    def t1(chunk):
        return T1Result([{"text": "Raj Patel", "type": "PERSON"}], "mreq_1", None)

    res = run_pipeline(doc, t1=t1)
    out = redact_pdf(doc.source, res.boxes)
    text = "".join(page.get_text() for page in pymupdf.open(stream=out, filetype="pdf"))
    assert "Patel" not in text
    assert "20-45-77" not in text and "31926819" not in text
    assert "Rent: 950 pounds per month" in text  # everything else stays
