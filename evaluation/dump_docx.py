"""Print every paragraph and table cell of a .docx in order. Run: venv/bin/python3 evaluation/dump_docx.py <file.docx>"""
import sys

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

doc = Document(sys.argv[1])
for child in doc.element.body.iterchildren():
    if child.tag.endswith("}p"):
        t = Paragraph(child, doc).text.strip()
        if t:
            print("P:", t)
    elif child.tag.endswith("}tbl"):
        tb = Table(child, doc)
        print(f"TABLE {len(tb.rows)}x{len(tb.columns)}")
        for row in tb.rows:
            print("   | " + " | ".join(c.text.strip().replace("\n", " / ")[:70] for c in row.cells))
