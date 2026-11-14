"""
Minimal report layout engine on reportlab.
- Tables and figures are numbered in the order they are declared in TABLE_ORDER / FIG_ORDER, and the build
  fails if they appear in the document in a different order, so in-text references cannot drift.
- Body font is DejaVu Sans (ships with matplotlib) so symbols such as >=, arrows and middle dots render.
"""
import os
import re
import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether, NextPageTemplate, Flowable)

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
for name, f in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
                ("DV-BI", "DejaVuSans-BoldOblique.ttf"), ("DVS", "DejaVuSerif.ttf"), ("DVS-B", "DejaVuSerif-Bold.ttf"),
                ("DVS-I", "DejaVuSerif-Italic.ttf"), ("DVS-BI", "DejaVuSerif-BoldItalic.ttf")):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, f)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")
pdfmetrics.registerFontFamily("DVS", normal="DVS", bold="DVS-B", italic="DVS-I", boldItalic="DVS-BI")

INK = colors.HexColor("#1f2933")
ACCENT = colors.HexColor("#1f4e79")
LIGHT = colors.HexColor("#e8eef5")
GRID = colors.HexColor("#b8c4d0")

ST = {
    "body": ParagraphStyle("body", fontName="DVS", fontSize=9.6, leading=14.2, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6),
    "h1": ParagraphStyle("h1", keepWithNext=1, fontName="DV-B", fontSize=16, leading=20, textColor=ACCENT, spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", keepWithNext=1, fontName="DV-B", fontSize=11.5, leading=15, textColor=ACCENT, spaceBefore=8, spaceAfter=5),
    "h3": ParagraphStyle("h3", keepWithNext=1, fontName="DV-B", fontSize=9.6, leading=13, textColor=INK, spaceBefore=4, spaceAfter=3),
    "bullet": ParagraphStyle("bullet", fontName="DVS", fontSize=9.4, leading=13.6, leftIndent=14, bulletIndent=3, textColor=INK, spaceAfter=2.5, alignment=TA_LEFT),
    "cap": ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=10.5, textColor=INK, spaceBefore=3, spaceAfter=9, alignment=TA_LEFT),
    "capt": ParagraphStyle("capt", fontName="DV-B", fontSize=8.2, leading=10.5, textColor=INK, spaceBefore=6, spaceAfter=3, alignment=TA_LEFT),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=7.4, leading=9.4, textColor=INK, alignment=TA_LEFT),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=7.4, leading=9.4, textColor=colors.white, alignment=TA_LEFT),
    "note": ParagraphStyle("note", fontName="DVS-I", fontSize=9, leading=13, textColor=INK, leftIndent=8, rightIndent=8, alignment=TA_JUSTIFY),
    "title": ParagraphStyle("title", fontName="DV-B", fontSize=24, leading=30, textColor=ACCENT, alignment=TA_LEFT),
    "sub": ParagraphStyle("sub", fontName="DV", fontSize=13, leading=18, textColor=INK, alignment=TA_LEFT),
    "meta": ParagraphStyle("meta", fontName="DV", fontSize=10, leading=15, textColor=INK, alignment=TA_LEFT),
}


class Marker(Flowable):
    """Zero-size flowable that records the page it lands on."""
    def __init__(self, key, store):
        super().__init__(); self.key, self.store = key, store; self.width = self.height = 0
    def draw(self):
        self.store[self.key] = self.canv.getPageNumber()


class Report:
    def __init__(self, path, table_order, fig_order, title, author):
        self.path, self.TO, self.FO = path, table_order, fig_order
        self.story, self.seen_t, self.seen_f, self.pages = [], [], [], {}
        self.title, self.author = title, author
        self.last_page = 0

    def _s(self, text):
        text = re.sub(r"@T:(\w+)@", lambda m: self.T(m.group(1)), str(text))
        return re.sub(r"@F:(\w+)@", lambda m: self.F(m.group(1)), text)

    # ---- numbering / references
    def T(self, key): return f"Table {self.TO.index(key) + 1}"
    def F(self, key): return f"Figure {self.FO.index(key) + 1}"

    # ---- flowables
    def h1(self, text, key=None, new_page=True):
        if new_page: self.story.append(PageBreak())
        if key: self.story.append(Marker(key, self.pages))
        self.story.append(Paragraph(text, ST["h1"]))
    def h2(self, text): self.story.append(Paragraph(text, ST["h2"]))
    def h3(self, text): self.story.append(Paragraph(text, ST["h3"]))
    def p(self, text): self.story.append(Paragraph(self._s(text), ST["body"]))
    def bullets(self, items):
        for it in items: self.story.append(Paragraph(self._s(it), ST["bullet"], bulletText="•"))
        self.story.append(Spacer(1, 4))
    def note(self, text):
        t = Table([[Paragraph(self._s(text), ST["note"])]], colWidths=[165 * mm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
                               ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        self.story += [t, Spacer(1, 8)]
    def space(self, h=6): self.story.append(Spacer(1, h))
    def pagebreak(self): self.story.append(PageBreak())

    def table(self, key, caption, rows, widths_mm, zebra=True, font=None):
        self.seen_t.append(key)
        n = self.TO.index(key) + 1
        data = []
        for i, r in enumerate(rows):
            style = ST["cellb"] if i == 0 else ST["cell"]
            data.append([Paragraph(self._s(c), style) for c in r])
        t = Table(data, colWidths=[w * mm for w in widths_mm], repeatRows=1)
        ts = [("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("GRID", (0, 0), (-1, -1), 0.4, GRID),
              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
              ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
        if zebra:
            ts += [("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f4f7fa")) for i in range(2, len(rows), 2)]
        t.setStyle(TableStyle(ts))
        cap = Paragraph(f"Table {n}. {self._s(caption)}", ST["capt"])
        if len(rows) <= 14:
            self.story.append(KeepTogether([cap, t, Spacer(1, 10)]))
        else:
            self.story += [cap, t, Spacer(1, 10)]

    def fig(self, key, path, caption, width_mm=150):
        self.seen_f.append(key)
        n = self.FO.index(key) + 1
        from PIL import Image as PILImage
        w, h = PILImage.open(path).size
        W = width_mm * mm
        img = Image(path, width=W, height=W * h / w)
        self.story.append(KeepTogether([img, Paragraph(f"Figure {n}. {self._s(caption)}", ST["cap"])]))

    # ---- build
    def _page(self, canv, doc):
        self.last_page = doc.page
        canv.saveState()
        if doc.page > 1:
            canv.setFont("DV", 7.5); canv.setFillColor(colors.HexColor("#5b6b7b"))
            canv.drawString(22 * mm, 12 * mm, f"{self.author}  ·  CloudServe Intelligent Support System")
            canv.drawRightString(A4[0] - 22 * mm, 12 * mm, f"{doc.page}")
            canv.setStrokeColor(GRID); canv.line(22 * mm, 16 * mm, A4[0] - 22 * mm, 16 * mm)
        canv.restoreState()

    def build(self):
        assert self.seen_t == self.TO, f"tables out of order or missing:\n declared {self.TO}\n seen     {self.seen_t}"
        assert self.seen_f == self.FO, f"figures out of order or missing:\n declared {self.FO}\n seen     {self.seen_f}"
        doc = BaseDocTemplate(self.path, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=22 * mm,
                              title=self.title, author=self.author)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
        doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._page)])
        doc.build(self.story)
        return self.pages
