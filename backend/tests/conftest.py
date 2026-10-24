import pymupdf
import pytest


def make_pdf(lines_per_page: list[list[str]]) -> bytes:
    """A small real PDF: each inner list is one page, each string one line of text."""
    doc = pymupdf.open()
    for lines in lines_per_page:
        page = doc.new_page()
        y = 72
        for line in lines:
            if line == "":
                y += 30  # blank line: a new text block
                continue
            page.insert_text((72, y), line, fontsize=11)
            y += 16
    return doc.tobytes()


@pytest.fixture
def tenancy_pdf() -> bytes:
    return make_pdf([
        ["Tenancy agreement", "", "Tenant: Raj Patel", "Address: 12 Oak Road, Leeds LS6 2AB", "",
         "Rent: 950 pounds per month"],
        ["Signed by Raj Patel", "Sort code 20-45-77, account no 31926819"],
    ])
