"""Data returned by ingest.extract()."""

from __future__ import annotations

from dataclasses import dataclass, field

# x0, y0, x1, y1 as fractions of the page width and height, origin at the top left.
BBox = tuple[float, float, float, float]

# Vision reports confidence in coarse steps (0.3, 0.5, 1.0); lines below this are flagged for review.
LOW_CONFIDENCE = 0.5


@dataclass
class Line:
    text: str
    bbox: BBox
    confidence: float  # 0 to 1; 1.0 for text taken from a PDF text layer
    angle: float = 0.0  # baseline direction in degrees, counterclockwise; 90 means the page lies on its side


@dataclass
class Page:
    number: int  # 1-based
    source: str  # "text_layer" or "ocr"
    text: str  # visual lines joined by "\n", paragraphs separated by a blank line
    lines: list[Line]
    rotation: float = 0.0  # degrees (counterclockwise) the page image was turned before the final OCR pass
    warnings: list[str] = field(default_factory=list)

    @property
    def low_confidence_lines(self) -> list[Line]:
        return [ln for ln in self.lines if ln.confidence < LOW_CONFIDENCE]


@dataclass
class Fix:
    page: int
    kind: str  # homoglyph, postcode, sort_code, iban, ni_number, digits, email
    before: str
    after: str


@dataclass
class ExtractedDocument:
    kind: str  # "pdf" or "image"
    pages: list[Page]
    fixes: list[Fix] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        """The whole document in the format T1 is trained on: pages and paragraphs separated by blank lines."""
        return "\n\n".join(p.text for p in self.pages if p.text)

    @property
    def used_ocr(self) -> bool:
        return any(p.source == "ocr" for p in self.pages)


class UnsupportedDocument(ValueError):
    """The bytes are not a PDF or an image we can read, or the PDF is encrypted or damaged."""


class OcrError(RuntimeError):
    """Apple Vision could not run (for example, not on macOS)."""
