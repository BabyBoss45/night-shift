"""Write the redacted PDF: true redaction (the text under each box is removed from the file),
not a black rectangle drawn on top of text that is still there."""

import pymupdf

from .pipeline import Box

PAD = 1.0  # points around each word box, so glyph edges do not peek out


def redact_pdf(source: bytes, boxes: list[Box]) -> bytes:
    pdf = pymupdf.open(stream=source, filetype="pdf")
    by_page: dict[int, list[Box]] = {}
    for b in boxes:
        by_page.setdefault(b.page, []).append(b)
    for pno, page_boxes in by_page.items():
        page = pdf[pno]
        for b in page_boxes:
            page.add_redact_annot(pymupdf.Rect(b.x0 - PAD, b.y0 - PAD, b.x1 + PAD, b.y1 + PAD), fill=(0, 0, 0))
        page.apply_redactions()
    return pdf.tobytes(garbage=3, deflate=True)
