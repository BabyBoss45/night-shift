"""Turn positioned text lines into reading-order text.

Pieces that share a visual row are joined with a space, left to right. Rows are
joined with "\n", and a blank line goes where the vertical gap between two rows is
large, which is how the T1 training documents separate paragraphs. A single column
of text is assumed: two-column layouts read row by row across both columns.
"""

from __future__ import annotations

from statistics import median

from .types import Line

SAME_ROW_OVERLAP = 0.5  # share of the shorter piece's height two pieces must overlap to be one row
PARAGRAPH_GAP = 0.8  # a gap above this many median row heights starts a new paragraph


def _height(line: Line) -> float:
    return max(line.bbox[3] - line.bbox[1], 1e-6)


def group_rows(lines: list[Line]) -> list[list[Line]]:
    """Group lines into visual rows, top to bottom; each row left to right."""
    rows: list[list[Line]] = []
    for line in sorted(lines, key=lambda ln: ((ln.bbox[1] + ln.bbox[3]) / 2, ln.bbox[0])):
        if rows:
            top = min(ln.bbox[1] for ln in rows[-1])
            bottom = max(ln.bbox[3] for ln in rows[-1])
            overlap = min(bottom, line.bbox[3]) - max(top, line.bbox[1])
            if overlap >= SAME_ROW_OVERLAP * min(_height(line), bottom - top):
                rows[-1].append(line)
                continue
        rows.append([line])
    for row in rows:
        row.sort(key=lambda ln: ln.bbox[0])
    return rows


def assemble(lines: list[Line]) -> str:
    rows = [row for row in group_rows([ln for ln in lines if ln.text.strip()])]
    if not rows:
        return ""
    heights = [max(ln.bbox[3] for ln in row) - min(ln.bbox[1] for ln in row) for row in rows]
    unit = median(heights)
    out: list[str] = []
    prev_bottom = None
    for row, height in zip(rows, heights):
        top = min(ln.bbox[1] for ln in row)
        if prev_bottom is not None and top - prev_bottom > PARAGRAPH_GAP * unit:
            out.append("")
        out.append(" ".join(ln.text.strip() for ln in row))
        prev_bottom = top + height
    return "\n".join(out)
