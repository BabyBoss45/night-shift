"""Photos and scans become PDF documents with a box for every word (app/ocrdoc.py).

Apple Vision only runs on macOS, so a fake reader stands in for it. Each test page carries three
colour marks; from them the fake works out how the image it is given was turned and scaled, and it
reports each text piece's box in that image, as Vision would. Everything else is the real ingest:
EXIF orientation, deskew, the 90/180/270 retries, layout and identifier repairs. The same marks give
the ground truth on the stored PDF page, independently of the mapping under test.
"""

import io
import logging
import math
from dataclasses import dataclass

import pymupdf
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageChops, ImageDraw, ImageFont

from app import ingest, ocrdoc
from app.extract import Document
from app.ingest import vision
from app.ingest.fixes import fix_identifiers
from app.ingest.layout import assemble
from app.ingest.types import ExtractedDocument, Line, Page
from app.main import app
from app.ocrdoc import document_from_ocr
from app.pdfout import redact_pdf
from app.pipeline import Box, T1Result

FONT = ImageFont.load_default(size=30)
_MEASURE = ImageDraw.Draw(Image.new("L", (1, 1)))


@dataclass
class Piece:
    x: int
    y: int
    text: str  # what is drawn
    ocr: str | None = None  # what the fake reader returns, if it misreads the drawing


class Scene:
    """An upright test page: black text pieces on white, and three colour marks near the corners."""

    def __init__(self, pieces, size=(1240, 1754), colours=((255, 0, 0), (0, 255, 0), (0, 0, 255))):
        self.pieces, self.size, self.colours = pieces, size, colours
        w, h = size
        self.marks = [(80, 80), (w - 80, 80), (80, h - 80)]

    def image(self) -> Image.Image:
        img = Image.new("RGB", self.size, "white")
        draw = ImageDraw.Draw(img)
        for (cx, cy), colour in zip(self.marks, self.colours):
            draw.rectangle((cx - 20, cy - 20, cx + 19, cy + 19), fill=colour)
        for p in self.pieces:
            draw.text((p.x, p.y), p.text, font=FONT, fill="black")
        return img

    def ink(self, piece):
        return _MEASURE.textbbox((piece.x, piece.y), piece.text, font=FONT)

    def words(self):
        """(word, upright ink box, piece) in reading order."""
        out = []
        for p in sorted(self.pieces, key=lambda p: (p.y, p.x)):
            pos = 0
            for word in p.text.split():
                s = p.text.index(word, pos)
                pos = s + len(word)
                left = p.x + _MEASURE.textlength(p.text[:s], font=FONT)
                out.append((word, _MEASURE.textbbox((left, p.y), word, font=FONT), p))
        return out

    def found_in(self, img) -> bool:
        return all(_mark(img, c) is not None for c in self.colours)

    def to_image(self, img):
        """Map upright page coordinates to pixels of img (any turn, scale or shift), from the marks."""
        (x0, y0), (x1, y1), (x2, y2) = self.marks
        (u0, v0), (u1, v1), (u2, v2) = (_mark(img, c) for c in self.colours)
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        inv = ((y2 - y0) / det, -(x2 - x0) / det, -(y1 - y0) / det, (x1 - x0) / det)
        a = (u1 - u0) * inv[0] + (u2 - u0) * inv[2]
        b = (u1 - u0) * inv[1] + (u2 - u0) * inv[3]
        c = (v1 - v0) * inv[0] + (v2 - v0) * inv[2]
        d = (v1 - v0) * inv[1] + (v2 - v0) * inv[3]

        def f(x, y):
            return u0 + a * (x - x0) + b * (y - y0), v0 + c * (x - x0) + d * (y - y0)

        return f, math.degrees(math.atan2(-c, a))  # Vision's baseline angle: counterclockwise, y up


def _mark(img, colour):
    bands = [band.point(lambda v, want=want: 255 if abs(v - want) < 70 else 0)
             for band, want in zip(img.convert("RGB").split(), colour)]
    box = ImageChops.multiply(ImageChops.multiply(bands[0], bands[1]), bands[2]).getbbox()
    return None if box is None else ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def _box_around(f, box):
    pts = [f(x, y) for x, y in ((box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]))]
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def fake_vision(*scenes, sideways=0.5):
    """Reads upright text with full confidence, text on its side with `sideways`, upside down not at all."""
    def recognize(img):
        scene = next((s for s in scenes if s.found_in(img)), None)
        if scene is None:  # a blank page
            return []
        to_img, angle = scene.to_image(img)
        folded = (angle + 180) % 360 - 180
        if abs(folded) > 135:
            return []
        conf = 1.0 if abs(folded) <= 45 else sideways
        lines = []
        for p in scene.pieces:
            x0, y0, x1, y1 = _box_around(to_img, scene.ink(p))
            lines.append(Line(text=p.ocr or p.text, bbox=(x0 / img.width, y0 / img.height, x1 / img.width, y1 / img.height),
                              confidence=conf, angle=angle))
        return lines
    return recognize


LETTER = Scene([
    Piece(150, 200, "Tenancy agreement"),
    Piece(150, 290, "Tenant: Oleksandra Kovalenko"),
    Piece(150, 326, "Address: 12 Oak Road, Leeds LS6 2AB", ocr="Address: 12 Oak Road, Leeds LS62AB"),
    Piece(150, 362, "Account:"),
    Piece(700, 362, "31926819", ocr="3l926819"),  # one row, two pieces; and a misread digit
    Piece(150, 450, "Signed by Raj Patel"),
])
SECOND = Scene([Piece(120, 200, "Page two for Ann Lee"), Piece(120, 236, "NI number QQ 12 34 56 C")],
               size=(1400, 1000), colours=((255, 0, 255), (255, 255, 0), (0, 255, 255)))
LETTER_TEXT = ("Tenancy agreement\n\nTenant: Oleksandra Kovalenko\nAddress: 12 Oak Road, Leeds LS6 2AB\n"
               "Account: 31926819\n\nSigned by Raj Patel")


def png(img, **kw):
    buf = io.BytesIO()
    img.save(buf, "PNG", **kw)
    return buf.getvalue()


def _render(page, zoom=2):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def _dark(img):
    """Pixels that are text ink: dark in every channel. The colour marks are painted out first, since
    resampling leaves a few dark pixels at their corners."""
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    for colour in LETTER.colours + SECOND.colours:
        found = _mark(img, colour)
        if found:
            draw.rectangle((found[0] - 40, found[1] - 40, found[0] + 40, found[1] + 40), fill="white")
    r, g, b = img.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v < 128 else 0)


def _embedded(pdf, page):
    pix = pymupdf.Pixmap(pdf, page.get_images()[0][0])
    if pix.n - pix.alpha != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def assert_offsets(doc: Document, text: str):
    assert doc.kind == "pdf" and doc.text == text
    assert [w.start for w in doc.words] == sorted(w.start for w in doc.words)
    for w in doc.words:
        assert doc.text[w.start:w.end] == w.text and w.text.strip() == w.text != ""


def assert_boxes_match_the_ink(doc: Document, scenes: list[Scene], tol=1.5):
    """Every word box covers that word's ink on the stored page, stays inside its line's ink box,
    and is not much wider than the word."""
    pdf = pymupdf.open(stream=doc.source, filetype="pdf")
    for pno, scene in enumerate(scenes):
        page = pdf[pno]
        f, _ = scene.to_image(_render(page))

        def to_points(box):
            x0, y0, x1, y1 = _box_around(f, box)
            return pymupdf.Rect(x0 / 2, y0 / 2, x1 / 2, y1 / 2) * page.derotation_matrix

        got = [w for w in doc.words if w.page == pno]
        expected = {word: (ink, piece) for word, ink, piece in scene.words()}  # the test words are unique
        assert sorted(w.text for w in got) == sorted(expected)
        for w in got:
            ink, piece = expected[w.text]
            want, line = to_points(ink), to_points(scene.ink(piece))
            x0, y0, x1, y1 = w.bbox
            assert x0 <= want.x0 + tol and y0 <= want.y0 + tol and x1 >= want.x1 - tol and y1 >= want.y1 - tol, w.text
            assert x0 >= line.x0 - tol and y0 >= line.y0 - tol and x1 <= line.x1 + tol and y1 <= line.y1 + tol, w.text
            char = max(line.width, line.height) / len(piece.text)
            assert max(x1 - x0, y1 - y0) <= max(want.width, want.height) + 5 * char + tol, w.text


def assert_redaction_removes_the_pixels(doc: Document):
    """Redact every word: no text ink is left in the embedded images, the rendered page is black
    under each box and unchanged elsewhere."""
    boxes = [Box(w.page, *w.bbox, type="TEST", placeholder="[X]", span_index=i) for i, w in enumerate(doc.words)]
    before = pymupdf.open(stream=doc.source, filetype="pdf")
    after = pymupdf.open(stream=redact_pdf(doc.source, boxes), filetype="pdf")
    assert after.page_count == before.page_count
    for pno in range(before.page_count):
        assert _dark(_embedded(after, after[pno])).getbbox() is None, f"text ink left in the image on page {pno}"
        page = before[pno]
        old, new = _render(page), _render(after[pno])
        covered = Image.new("L", old.size, 0)
        draw = ImageDraw.Draw(covered)
        for b in boxes:
            if b.page != pno:
                continue
            r = pymupdf.Rect(b.x0, b.y0, b.x1, b.y1) * page.rotation_matrix * 2
            assert max(new.crop((round(r.x0) + 2, round(r.y0) + 2, round(r.x1) - 2, round(r.y1) - 2)).getextrema()[0]) <= 30
            draw.rectangle((r.x0 - 6, r.y0 - 6, r.x1 + 6, r.y1 + 6), fill=255)
        diff = ImageChops.difference(old, new).convert("L").point(lambda v: 255 if v > 40 else 0)
        assert ImageChops.subtract(diff, covered).getbbox() is None, f"page {pno} changed outside the boxes"


@pytest.fixture
def letter_vision(monkeypatch):
    monkeypatch.setattr(vision, "recognize", fake_vision(LETTER, SECOND))


# Building words from ingest's lines -------------------------------------------------------------


def _line(text, x0, y0, x1, y1, angle=0.0):
    return Line(text=text, bbox=(x0, y0, x1, y1), confidence=1.0, angle=angle)


def test_words_get_offsets_into_ingest_text_and_boxes_inside_their_line(monkeypatch):
    lines = [_line("Account:", 0.1, 0.30, 0.3, 0.34), _line("3l926819", 0.5, 0.302, 0.8, 0.342),
             _line("Dear Ann Lee,", 0.1, 0.10, 0.5, 0.14), _line("Kind regards", 0.1, 0.60, 0.5, 0.64)]
    text, fixes = fix_identifiers(assemble(lines), 1)
    assert fixes and text == "Dear Ann Lee,\n\nAccount: 31926819\n\nKind regards"
    page = Page(number=1, source="ocr", text=text, lines=lines)
    monkeypatch.setattr(ingest, "extract", lambda data: ExtractedDocument(kind="image", pages=[page]))
    doc = document_from_ocr(png(Image.new("RGB", (1000, 500), "white")), "photo.png")

    assert_offsets(doc, text)
    assert doc.pages == [(1000.0, 500.0)]  # no dpi: one pixel per point
    assert [w.text for w in doc.words] == ["Dear", "Ann", "Lee,", "Account:", "31926819", "Kind", "regards"]
    boxes = {ln.text: (ln.bbox[0] * 1000, ln.bbox[1] * 500, ln.bbox[2] * 1000, ln.bbox[3] * 500) for ln in lines}
    by_text = {"Dear": "Dear Ann Lee,", "Ann": "Dear Ann Lee,", "Lee,": "Dear Ann Lee,", "Account:": "Account:",
               "31926819": "3l926819", "Kind": "Kind regards", "regards": "Kind regards"}
    for w in doc.words:
        x0, y0, x1, y1 = boxes[by_text[w.text]]
        assert x0 - 1e-6 <= w.bbox[0] < w.bbox[2] <= x1 + 1e-6 and y0 - 1e-6 <= w.bbox[1] < w.bbox[3] <= y1 + 1e-6
    keys = {w.text: w.line for w in doc.words}
    assert keys["Ann"] == keys["Lee,"] != keys["Account:"] != keys["31926819"]  # one key per OCR line
    left, right = (next(w.bbox for w in doc.words if w.text == t) for t in ("Dear", "Lee,"))
    assert left[0] == pytest.approx(100) and right[2] == pytest.approx(500) and left[2] < right[0]


def test_a_line_missing_from_the_text_is_skipped_and_counted(monkeypatch, caplog):
    lines = [_line("Dear Ann", 0.1, 0.1, 0.5, 0.14), _line("Gone line", 0.1, 0.15, 0.5, 0.19),
             _line("Kind regards", 0.1, 0.20, 0.5, 0.24)]
    page = Page(number=1, source="ocr", text="Dear Ann\nKind regards", lines=lines)
    monkeypatch.setattr(ingest, "extract", lambda data: ExtractedDocument(kind="image", pages=[page]))
    with caplog.at_level(logging.WARNING, logger="app.ocrdoc"):
        doc = document_from_ocr(png(Image.new("RGB", (800, 600), "white")), "photo.png")
    assert_offsets(doc, "Dear Ann\nKind regards")
    assert [w.text for w in doc.words] == ["Dear", "Ann", "Kind", "regards"]
    assert "1 of 3 lines" in caplog.text
    assert "Ann" not in caplog.text  # counts only, never document text


def test_if_boxes_fail_the_document_is_kept_as_text(monkeypatch, letter_vision, caplog):
    def broken(*_args):
        raise RuntimeError("boom")

    monkeypatch.setattr(ocrdoc, "_words", broken)
    doc = document_from_ocr(png(LETTER.image()), "photo.png")
    assert doc.kind == "text" and doc.text == LETTER_TEXT and doc.words == []
    assert "RuntimeError" in caplog.text


# Photos and scans, through the real ingest with the fake reader ----------------------------------


def test_photo_words_are_boxed_on_a_pdf_page_and_redaction_removes_the_pixels(letter_vision):
    doc = document_from_ocr(png(LETTER.image(), dpi=(150, 150)), "photo.png")
    assert_offsets(doc, LETTER_TEXT)  # the repaired account number and postcode, as T1 sees them
    assert doc.pages == [pytest.approx((1240 * 72 / 150, 1754 * 72 / 150), rel=1e-3)]
    assert pymupdf.open(stream=doc.source, filetype="pdf").page_count == 1
    assert_boxes_match_the_ink(doc, [LETTER])
    assert_redaction_removes_the_pixels(doc)


@pytest.mark.parametrize(("turn", "rotation"), [(90, 270.0), (180, 180.0), (270, 90.0), (3.0, 357.0), (-2.0, 2.0)],
                         ids=["90", "180", "270", "deskew+3", "deskew-2"])
def test_turned_and_skewed_photos_map_back(letter_vision, turn, rotation):
    stored = LETTER.image().rotate(turn, resample=Image.BICUBIC, expand=True, fillcolor="white")
    data = png(stored, dpi=(150, 150))
    assert ingest.extract(data).pages[0].rotation == rotation  # ingest really turned it before the final read
    doc = document_from_ocr(data, "photo.png")
    assert_offsets(doc, LETTER_TEXT)
    assert doc.pages == [pytest.approx((stored.width * 72 / 150, stored.height * 72 / 150), rel=1e-3)]
    assert_boxes_match_the_ink(doc, [LETTER])
    assert_redaction_removes_the_pixels(doc)


def test_a_page_read_on_its_side_is_split_along_its_lines(monkeypatch):
    # When Vision reads sideways text as well as upright text, ingest keeps its first good turn (90):
    # the final lines run top to bottom (angle -90), so words are placed down the line box.
    monkeypatch.setattr(vision, "recognize", fake_vision(LETTER, sideways=1.0))
    data = png(LETTER.image().rotate(180), dpi=(150, 150))
    page = ingest.extract(data).pages[0]
    assert page.rotation == 90.0 and round(page.lines[0].angle) == -90
    doc = document_from_ocr(data, "photo.png")
    assert_offsets(doc, ingest.extract(data).text)  # ingest's rows run across the sideways lines: odd text, still exact
    assert_boxes_match_the_ink(doc, [LETTER])
    assert_redaction_removes_the_pixels(doc)


def test_exif_rotated_jpeg_becomes_an_upright_page(letter_vision):
    small = LETTER.image().resize((930, 1316))  # under ingest's MIN_WIDTH: it scales up before OCR
    exif = Image.Exif()
    exif[0x0112] = 6  # a phone stores the pixels turned and records Orientation=6
    buf = io.BytesIO()
    small.rotate(90, expand=True).save(buf, "JPEG", quality=95, exif=exif, dpi=(100, 100))
    assert ingest.extract(buf.getvalue()).pages[0].rotation == 0.0
    doc = document_from_ocr(buf.getvalue(), "IMG_0001.JPG")
    assert_offsets(doc, LETTER_TEXT)
    assert doc.pages == [pytest.approx((930 * 72 / 100, 1316 * 72 / 100), rel=1e-3)]  # portrait, as shown
    assert all(w.bbox[3] < 300 for w in doc.words)  # the text sits near the top of the upright page
    assert_boxes_match_the_ink(doc, [LETTER])  # the marks also carry the scale
    assert_redaction_removes_the_pixels(doc)


def test_jpeg_without_orientation_is_embedded_as_uploaded(letter_vision):
    buf = io.BytesIO()
    LETTER.image().save(buf, "JPEG", quality=90, dpi=(150, 150))
    doc = document_from_ocr(buf.getvalue(), "scan.jpg")
    pdf = pymupdf.open(stream=doc.source, filetype="pdf")
    assert pdf.extract_image(pdf[0].get_images()[0][0])["image"] == buf.getvalue()
    assert_boxes_match_the_ink(doc, [LETTER])
    assert_redaction_removes_the_pixels(doc)


def test_multi_frame_tiff_gives_one_page_per_frame(letter_vision):
    buf = io.BytesIO()
    LETTER.image().save(buf, "TIFF", save_all=True, append_images=[SECOND.image()], dpi=(150, 150))
    doc = document_from_ocr(buf.getvalue(), "scan.tiff")
    assert_offsets(doc, LETTER_TEXT + "\n\nPage two for Ann Lee\nNI number QQ 12 34 56 C")
    assert doc.pages == [pytest.approx((1240 * 0.48, 1754 * 0.48), rel=1e-3), pytest.approx((1400 * 0.48, 1000 * 0.48), rel=1e-3)]
    assert {w.page for w in doc.words} == {0, 1}
    assert_boxes_match_the_ink(doc, [LETTER, SECOND])
    assert_redaction_removes_the_pixels(doc)


def test_scanned_pdf_keeps_its_bytes(letter_vision):
    buf = io.BytesIO()
    LETTER.image().save(buf, "PDF", resolution=150, save_all=True, append_images=[SECOND.image()])
    data = buf.getvalue()
    assert [p.source for p in ingest.extract(data).pages] == ["ocr", "ocr"]
    doc = document_from_ocr(data, "scan.pdf")
    assert doc.source == data
    assert_offsets(doc, LETTER_TEXT + "\n\nPage two for Ann Lee\nNI number QQ 12 34 56 C")
    assert_boxes_match_the_ink(doc, [LETTER, SECOND])
    assert_redaction_removes_the_pixels(doc)


@pytest.mark.parametrize("pdf_rotate", [90, 270])
def test_scanned_pdf_page_with_its_own_rotate(letter_vision, pdf_rotate):
    # The scanner stored the page sideways and set /Rotate: ingest reads the page as shown, the boxes
    # must land in the page's own (unrotated) frame, where PyMuPDF redacts.
    sideways = LETTER.image().rotate(-pdf_rotate, expand=True)
    pdf = pymupdf.open()
    page = pdf.new_page(width=sideways.width * 0.48, height=sideways.height * 0.48)
    page.insert_image(page.rect, stream=png(sideways))
    page.set_rotation(pdf_rotate)
    data = pdf.tobytes()
    doc = document_from_ocr(data, "scan.pdf")
    assert_offsets(doc, LETTER_TEXT)
    assert doc.pages == [pytest.approx((1240 * 0.48, 1754 * 0.48))]  # as shown, like extract.py
    assert_boxes_match_the_ink(doc, [LETTER])
    assert_redaction_removes_the_pixels(doc)


def test_text_layer_pages_also_get_boxes(monkeypatch):
    def no_ocr(_image):
        raise AssertionError("a page with a text layer is not read with OCR")

    monkeypatch.setattr(vision, "recognize", no_ocr)
    pdf = pymupdf.open()
    page = pdf.new_page()
    page.insert_text((72, 100), "Tenant: Raj Patel, sort code 20-45-77, account 31926819, rent 950 pounds a month.", fontsize=9)
    page.insert_text((72, 120), "The landlord keeps the deposit in a scheme and returns it at the end of the term.", fontsize=9)
    doc = document_from_ocr(pdf.tobytes(), "lease.pdf")
    assert doc.text.startswith("Tenant: Raj Patel,")
    assert_offsets(doc, doc.text)
    target = [w for w in doc.words if w.text in ("Raj", "Patel,")]
    boxes = [Box(w.page, *w.bbox, type="PERSON", placeholder="[PERSON_1]", span_index=0) for w in target]
    out = pymupdf.open(stream=redact_pdf(doc.source, boxes), filetype="pdf")[0].get_text()
    assert "Patel" not in out and "Raj" not in out
    # word boxes reach PAD_CHARS past each word, so a neighbouring character or two goes as well
    assert "code 20-45-77, account 31926819" in out and "returns it at the end of the term." in out


# Through the API ----------------------------------------------------------------------------------


@pytest.fixture
def client(letter_vision):
    def t1_factory(doc_id):
        def t1(chunk):
            return T1Result([{"text": "Raj Patel", "type": "PERSON"}] if "Raj Patel" in chunk else [], "mreq_test", None)
        return t1

    app.state.t1_factory = t1_factory
    yield TestClient(app)
    app.state.t1_factory = None


def test_photo_upload_gives_boxes_and_a_redacted_pdf(client):
    doc = client.post("/api/documents", files={"file": ("photo.png", png(LETTER.image(), dpi=(150, 150)), "image/png")}).json()
    assert doc["kind"] == "pdf" and doc["text"] == LETTER_TEXT and len(doc["pages"]) == 1
    res = client.post(f"/api/documents/{doc['doc_id']}/redact").json()
    assert {e["text"] for e in res["entities"]} >= {"Raj Patel", "31926819", "LS6 2AB"}
    assert res["boxes"] and {b["page"] for b in res["boxes"]} == {0}
    assert client.get(f"/api/documents/{doc['doc_id']}/pages/0.png").content[:4] == b"\x89PNG"
    out = client.get(f"/api/documents/{doc['doc_id']}/file")
    assert out.headers["content-type"] == "application/pdf"
    assert 'filename="photo-redacted.pdf"' in out.headers["content-disposition"]

    pdf = pymupdf.open(stream=out.content, filetype="pdf")
    image = _embedded(pdf, pdf[0])
    f, _ = LETTER.to_image(image)
    dark = _dark(image)
    for word, ink, _piece in LETTER.words():
        has_ink = dark.crop(tuple(round(v) for v in _box_around(f, ink))).getbbox() is not None
        assert has_ink == (word not in ("Raj", "Patel", "31926819", "LS6", "2AB")), word


def test_blank_photo_says_no_text_was_found(client):
    blank = png(Image.new("RGB", (1240, 1754), "white"))
    r = client.post("/api/documents", files={"file": ("blank.png", blank, "image/png")})
    assert r.status_code == 400 and r.json()["detail"] == "No text was found in this file."
