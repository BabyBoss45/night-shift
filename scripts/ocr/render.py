"""Render dataset documents as PDFs and page images, and degrade the images like real scans and photos.

Used by eval_ocr.py to measure how much personal data survives ingest.extract().
"""

from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental/"
FONTS = ["Arial.ttf", "Times New Roman.ttf", "Georgia.ttf", "Courier New.ttf"]
DPI = 300
PAGE_W, PAGE_H, MARGIN = 2480, 3508, 220  # A4 at 300 dpi
FONT_PX = 46  # 11 pt at 300 dpi
LINE_PX = 58


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    out, line = [], ""
    for word in text.split(" "):
        cand = f"{line} {word}" if line else word
        if draw.textlength(cand, font=font) <= max_w or not line:
            line = cand
        else:
            out.append(line)
            line = word
    out.append(line)
    return out


def render_pages(text: str, font_name: str, max_pages: int) -> tuple[list[Image.Image], int]:
    """Draw whole source lines onto A4 pages. Returns the pages and how many characters of text were drawn."""
    font = ImageFont.truetype(FONT_DIR + font_name, FONT_PX)
    pages: list[Image.Image] = []
    page, draw, y, drawn, pos = None, None, 0, 0, 0
    for src_line in text.split("\n"):
        wrapped = _wrap(ImageDraw.Draw(Image.new("L", (1, 1))), src_line, font, PAGE_W - 2 * MARGIN) if src_line else [""]
        if page is None or y + LINE_PX * len(wrapped) > PAGE_H - MARGIN:
            if len(pages) == max_pages:
                break
            page = Image.new("L", (PAGE_W, PAGE_H), 255)
            draw, y = ImageDraw.Draw(page), MARGIN
            pages.append(page)
        for ln in wrapped:
            draw.text((MARGIN, y), ln, font=font, fill=0)
            y += LINE_PX
        pos += len(src_line) + 1
        drawn = min(pos, len(text))
    return pages, drawn


def text_layer_pdf(text: str) -> bytes:
    """A PDF with a real text layer (Helvetica 11 pt), source lines wrapped to the page."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 780
    for src_line in text.split("\n"):
        words, line, lines = src_line.split(" "), "", []
        for word in words:
            cand = f"{line} {word}" if line else word
            if stringWidth(cand, "Helvetica", 11) <= 450 or not line:
                line = cand
            else:
                lines.append(line)
                line = word
        lines.append(line)
        for ln in lines:
            if y < 60:
                c.showPage()
                y = 780
            c.setFont("Helvetica", 11)
            c.drawString(72, y, ln)
            y -= 15
    c.save()
    return buf.getvalue()


def image_pdf(pages: list[Image.Image], dpi: int) -> bytes:
    buf = io.BytesIO()
    rgb = [p.convert("RGB") for p in pages]
    rgb[0].save(buf, "PDF", resolution=dpi, save_all=True, append_images=rgb[1:])
    return buf.getvalue()


def _jpeg(img: Image.Image, quality: int) -> Image.Image:
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    return Image.open(io.BytesIO(buf.getvalue())).convert("L")


def _noise(img: Image.Image, sigma: float, rng: np.random.Generator) -> Image.Image:
    arr = np.asarray(img, dtype=float) + rng.normal(0, sigma, (img.height, img.width))
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def _perspective(src, dst):
    rows = []
    for (x, y), (u, v) in zip(dst, src):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    return np.linalg.solve(np.array(rows, dtype=float), np.array(src, dtype=float).reshape(8)).tolist()


def degrade(img: Image.Image, level: str, seed: int) -> tuple[Image.Image, int]:
    """Return the degraded page and its effective dpi."""
    rng = np.random.default_rng(seed)
    w, h = img.size
    if level == "clean_scan":
        return img, DPI
    if level == "sideways":
        return img.rotate(90, expand=True), DPI
    if level == "office_scan":
        out = img.rotate(float(rng.uniform(-1.5, 1.5)), resample=Image.BICUBIC, fillcolor=255)
        out = _noise(out.filter(ImageFilter.GaussianBlur(0.8)), 12, rng)
        return _jpeg(out.resize((w * 2 // 3, h * 2 // 3), Image.BILINEAR), 40), 200
    if level == "low_res_scan":
        out = _noise(img.filter(ImageFilter.GaussianBlur(1.0)), 10, rng)
        return _jpeg(out.resize((w // 2, h // 2), Image.BILINEAR), 50), 150
    if level == "phone_photo":
        dst = [(int(rng.uniform(40, 160)), int(rng.uniform(40, 260))), (w - int(rng.uniform(20, 120)), int(rng.uniform(20, 120))),
               (w - int(rng.uniform(60, 200)), h - int(rng.uniform(20, 120))), (int(rng.uniform(20, 120)), h - int(rng.uniform(80, 240)))]
        out = img.transform((w, h), Image.PERSPECTIVE, _perspective([(0, 0), (w, 0), (w, h), (0, h)], dst),
                            Image.BICUBIC, fillcolor=255)
        out = out.rotate(float(rng.uniform(-4, 4)), resample=Image.BICUBIC, fillcolor=255)
        light = np.linspace(rng.uniform(0.5, 0.7), 1.0, w)[None, :] * np.linspace(rng.uniform(0.7, 0.9), 1.0, h)[:, None]
        out = Image.fromarray(np.clip(np.asarray(out, dtype=float) * light + 25, 0, 255).astype("uint8"))
        out = _noise(out.filter(ImageFilter.GaussianBlur(1.3)), 16, rng)
        return _jpeg(out.resize((w // 2, h // 2), Image.BILINEAR), 35), 150
    raise ValueError(level)
