"""
Build docs/architecture.drawio (three pages) from one layout definition, check it for overlaps, and render a PNG preview
of the same geometry so the layout can be inspected without draw.io.

  Page 1  High-level architecture   six components over three cross-cutting concerns   (brief, high-level figure)
  Page 2  Low-level design          application / model and retrieval / persistence    (brief, low-level figure)
  Page 3  Routing decision tree     every rule in src/pipeline.py and src/route.py     (brief, routing figure)

Run: venv/bin/python3 docs/make_drawio.py
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.join(HERE, "report", "fig")

COL = {  # kind: (fill, stroke)
    "flow": ("#d5e8d4", "#82b366"), "policy": ("#fff2cc", "#d6b656"), "human": ("#f8cecc", "#b85450"),
    "store": ("#e1d5e7", "#9673a6"), "api": ("#dae8fc", "#6c8ebf"), "ctrl": ("#fde9d9", "#e8660b"),
    "start": ("#1f2933", "#1f2933"), "ok": ("#cfe8d5", "#4c9a6a"), "grey": ("#eeeeee", "#8a97a6"),
    "lane": ("#f6f7f9", "#b8c4d0"), "lane2": ("#fdf3ea", "#f0c9a8"),
}
EDGE = {"main": "#1f2933", "red": "#b85450", "green": "#4c9a6a", "purple": "#9673a6", "orange": "#e8660b", "grey": "#8a97a6"}

pages = []   # each: {"name", "w", "h", "nodes": [], "edges": []}


def page(name, w, h):
    p = {"name": name, "w": w, "h": h, "nodes": [], "edges": []}
    pages.append(p)
    return p


def node(p, nid, x, y, w, h, text, kind="flow", shape="box", bold_first=True, fs=12, align="center"):
    p["nodes"].append(dict(id=nid, x=x, y=y, w=w, h=h, text=text, kind=kind, shape=shape, bold_first=bold_first, fs=fs, align=align))


def edge(p, src, dst, label="", color="main", dashed=False, exit=None, entry=None, via=None):
    p["edges"].append(dict(src=src, dst=dst, label=label, color=color, dashed=dashed, exit=exit, entry=entry, via=via or []))


# ====================================================================== page 1: high level
p1 = page("1 High-level architecture", 1110, 480)
node(p1, "title", 20, 6, 760, 26, "High-level architecture: six processing components over three cross-cutting concerns", "grey", "text", fs=15, align="left")
node(p1, "chan", 20, 50, 150, 70, "Input channels\nemail, chat,\ndocs_comment, forum", "api", fs=11)
node(p1, "esc", 560, 50, 330, 60, "Escalate to a human\nsummary, sources, reason code", "human", fs=11)
node(p1, "auto", 980, 50, 100, 60, "Auto reply\nwith citations", "ok", fs=11)
steps = [("ing", "1 INGEST", "kill switch, normalise,\ninjection and security-\nwording screen", "flow"),
         ("cls", "2 CLASSIFY", "intent, urgency,\ncalibrated confidence\n(nearest tickets, LLM\nif unsure)", "flow"),
         ("ret", "3 RETRIEVE", "hybrid search\n(dense + BM25) over\nthe 29 articles", "flow"),
         ("rou", "4 ROUTE", "deterministic rules:\nsafety, confidence 0.85,\nevidence", "policy"),
         ("gen", "5 GENERATE", "draft from the full\ntop article, with\ncitations", "flow"),
         ("val", "6 VALIDATE", "guardrails: PII,\ngrounding, figures,\ninjection, tone", "policy")]
for i, (nid, title, body, kind) in enumerate(steps):
    node(p1, nid, 20 + i * 180, 160, 150, 100, f"{title}\n{body}", kind, fs=11)
for a, b in zip(steps, steps[1:]):
    edge(p1, a[0], b[0], exit=(1, .5), entry=(0, .5))
edge(p1, "chan", "ing", exit=(.5, 1), entry=(.5, 0))
edge(p1, "rou", "esc", "escalate", "red", exit=(.5, 0), entry=(.2, 1))
edge(p1, "gen", "esc", "NO_ANSWER", "red", exit=(.5, 0), entry=(.8, 1))
edge(p1, "val", "auto", "all pass", "green", exit=(.5, 0), entry=(.5, 1))
edge(p1, "val", "esc", "blocked", "red", exit=(.2, 0), entry=(1, .5), via=[(950, 80)])
node(p1, "log", 20, 330, 330, 80, "AUDIT LOG\nevery decision recorded with its reasoning\n(SQLite: decisions, alternatives, sources)", "store", fs=11)
node(p1, "mon", 385, 330, 330, 80, "MONITORING\nlatency, volume, drift\n(Prometheus, Grafana, alert rules)", "store", fs=11)
node(p1, "fb", 750, 330, 330, 80, "FEEDBACK LOOP\nhuman corrections return (POST /feedback)\nand join the classifier's neighbour index", "ctrl", fs=11)
edge(p1, "cls", "log", "", "purple", True, exit=(.5, 1), entry=(.5, 0))
edge(p1, "rou", "mon", "", "purple", True, exit=(.5, 1), entry=(.5, 0))
edge(p1, "val", "fb", "", "orange", True, exit=(.5, 1), entry=(.5, 0))
node(p1, "foot", 20, 430, 1060, 30, "Dashed arrows: each step writes to the audit log and the metrics, and a human correction feeds the next classification.", "grey", "text", fs=10, align="left")

# ====================================================================== page 2: low level
p2 = page("2 Low-level design", 1130, 700)
node(p2, "title", 20, 6, 800, 26, "Low-level component design: three layers", "grey", "text", fs=15, align="left")
lanes = [("L1", 44, "APPLICATION LAYER", "lane"), ("L2", 262, "MODEL AND RETRIEVAL LAYER", "lane2"), ("L3", 480, "PERSISTENCE AND OBSERVABILITY LAYER", "lane")]
for lid, y, name, kind in lanes:
    node(p2, lid, 20, y, 1090, 190, name, kind, "lane", fs=12)
X = [40, 310, 580, 850]
row = lambda ly: ly + 62
app = [("fast", "FastAPI\nPOST /tickets, POST /feedback\nGET /decisions, /health, /metrics\nPOST /admin/kill-switch", "api"),
       ("orch", "Orchestrator\nLangGraph state machine\n(src/pipeline.py)", "flow"),
       ("guard", "Guardrail step (validate)\nPII, grounding, figures,\ninjection, tone: can block", "policy"),
       ("fmt", "Response formatter\n(src/formatter.py)\nreply + citations, or\nescalation packet", "flow")]
mod = [("clf", "Classifier chain\nnearest labelled tickets,\nthen few-shot LLM prompt\n(PR-CL-01 v2.0)", "flow"),
       ("emb", "Embedding model\nall-MiniLM-L6-v2\n(local)", "flow"),
       ("chroma", "Chroma vector store\nhybrid search: dense + BM25\narticles + labelled tickets", "store"),
       ("genc", "Generator chain: JSON output\n(status, answer, cited_docs)\nPR-GN-01 v4.0, LLM via OpenRouter\nor any OpenAI-compatible provider", "flow")]
per = [("db", "SQLite decision log\ndecisions, resolution records,\nfeedback (PostgreSQL\nwould be a drop-in change)", "store"),
       ("prom", "Prometheus\nmetrics and alert rules", "store"),
       ("graf", "Grafana\ndashboards (9 panels)", "store"),
       ("ci", "GitHub Actions\nCI pipeline\n(tests and harness)", "store")]
for (lid, ly, _, _), items in zip(lanes, (app, mod, per)):
    for x, (nid, text, kind) in zip(X, items):
        node(p2, nid, x, row(ly), 220, 100, text, kind, fs=11)
for items in (app, mod, per):
    for a, b in zip(items, items[1:]):
        edge(p2, a[0], b[0], exit=(1, .5), entry=(0, .5)) if items is not per else None
edge(p2, "orch", "emb", "", "grey", True, exit=(.5, 1), entry=(.5, 0))
edge(p2, "chroma", "guard", "sources shown to the guardrails", "grey", True, exit=(.5, 0), entry=(.5, 1))
edge(p2, "clf", "db", "every decision", "purple", True, exit=(.5, 1), entry=(.5, 0))
edge(p2, "prom", "graf", "", "purple", False, exit=(1, .5), entry=(0, .5))
node(p2, "foot", 20, 676, 1090, 20, "Solid arrows: data flow. Dashed: calls and logging between layers.", "grey", "text", fs=10, align="left")

# ====================================================================== page 3: routing tree
p3 = page("3 Routing decision tree", 1000, 1300)
node(p3, "title", 20, 6, 900, 26, "Routing decision tree: first matching rule wins, every branch is logged with its reason code", "grey", "text", fs=15, align="left")
CX, DW, DH = 330, 340, 90
node(p3, "t0", CX - 130, 50, 260, 46, "Ticket arrives", "start", fs=12)
dec = [("d1", "Kill switch on?", "kill_switch"),
       ("d2", "Injection or security wording\nin the ticket?", "injection_screen, safety_keyword"),
       ("d3", "Intent is security, compliance,\nfeature request or unclear?", "safety_intent"),
       ("d4", "Restricted topics among nearest\ntickets (weight 0.10 or more)?", "safety_proximity"),
       ("d5", "Confidence below 0.85?", "low_confidence"),
       ("d6", "No article above the\nrelevance floor (0.30)?", "no_passages")]
y = 128
prev = "t0"
for nid, text, code in dec:
    node(p3, nid, CX - DW // 2, y, DW, DH, text, "policy", "diamond", fs=11)
    node(p3, "e_" + nid, 660, y + 20, 310, 50, f"Escalate to a human\nreason code: {code}", "human", fs=11)
    edge(p3, prev, nid, "" if prev == "t0" else "no", exit=(.5, 1), entry=(.5, 0))
    edge(p3, nid, "e_" + nid, "yes", "red", exit=(1, .5), entry=(0, .5))
    prev, y = nid, y + 120
node(p3, "g1", CX - 140, y, 280, 50, "Generate a JSON reply from the\nfull top article (PR-GN-01 v4.0)", "flow", fs=11)
edge(p3, prev, "g1", "no", exit=(.5, 1), entry=(.5, 0))
y += 80
node(p3, "d7", CX - DW // 2, y, DW, DH, "Model answered NO_ANSWER?", "policy", "diamond", fs=11)
node(p3, "e_d7", 660, y + 20, 310, 50, "Escalate to a human\nreason code: model_declined", "human", fs=11)
edge(p3, "g1", "d7", exit=(.5, 1), entry=(.5, 0))
edge(p3, "d7", "e_d7", "yes", "red", exit=(1, .5), entry=(0, .5))
y += 110
node(p3, "d8", CX - DW // 2, y, DW, DH, "Does any guardrail block\nthe draft?", "policy", "diamond", fs=11)
node(p3, "e_d8", 660, y + 20, 310, 50, "Block and escalate to a human\nreason code: guardrail_block", "human", fs=11)
edge(p3, "d7", "d8", "no", exit=(.5, 1), entry=(.5, 0))
edge(p3, "d8", "e_d8", "yes", "red", exit=(1, .5), entry=(0, .5))
y += 110
node(p3, "send", CX - 140, y, 280, 50, "Send the reply with its citations\n(reason code: confident_and_grounded)", "ok", fs=11)
edge(p3, "d8", "send", "no", "green", exit=(.5, 1), entry=(.5, 0))
node(p3, "note", 20, y + 80, 950, 44, "Every escalation carries a summary, the retrieved sources and the reason code, and every decision is written to the audit log. "
     "Rules 1 to 2 run before any model sees the ticket; rules 3 to 6 follow the brief's tree (confidence, then evidence) with the safety rules added in front.", "grey", "text", fs=10, align="left")


# ====================================================================== geometry helpers
def anchor(n, frac):
    return (n["x"] + frac[0] * n["w"], n["y"] + frac[1] * n["h"])


def route(p, e, nodes):
    s, d = nodes[e["src"]], nodes[e["dst"]]
    a = anchor(s, e["exit"]) if e["exit"] else (s["x"] + s["w"] / 2, s["y"] + s["h"] / 2)
    b = anchor(d, e["entry"]) if e["entry"] else (d["x"] + d["w"] / 2, d["y"] + d["h"] / 2)
    return [a] + list(e["via"]) + [b]


def check_overlaps(p):
    boxes = [n for n in p["nodes"] if n["shape"] not in ("lane", "text")]
    bad = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
                bad.append((a["id"], b["id"]))
    for n in p["nodes"]:
        if n["x"] < 0 or n["y"] < 0 or n["x"] + n["w"] > p["w"] or n["y"] + n["h"] > p["h"]:
            bad.append((n["id"], "outside page"))
    nodes = {n["id"]: n for n in p["nodes"]}
    for e in p["edges"]:  # an edge must not pass through a third box
        pts = route(p, e, nodes)
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            for n in boxes:
                if n["id"] in (e["src"], e["dst"]):
                    continue
                if min(x1, x2) < n["x"] + n["w"] and max(x1, x2) > n["x"] and min(y1, y2) < n["y"] + n["h"] and max(y1, y2) > n["y"]:
                    bad.append((f"edge {e['src']}->{e['dst']}", f"crosses {n['id']}"))
    return bad


# ====================================================================== drawio xml
def style(n):
    f, s = COL[n["kind"]]
    if n["shape"] == "text":
        return f"text;html=1;align={n['align']};verticalAlign=middle;fontSize={n['fs']};fontStyle=1;strokeColor=none;fillColor=none;whiteSpace=wrap;"
    if n["shape"] == "lane":
        return f"rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;fontStyle=1;fontSize={n['fs']};fillColor={f};strokeColor={s};fontColor=#4a4a68;"
    base = "rhombus;" if n["shape"] == "diamond" else "rounded=1;arcSize=8;"
    fc = "fontColor=#ffffff;" if n["kind"] == "start" else ""
    return f"{base}whiteSpace=wrap;html=1;fontSize={n['fs']};fillColor={f};strokeColor={s};strokeWidth=1.5;{fc}"


def value(n):
    lines = n["text"].split("\n")
    if n["shape"] in ("box",) and n["bold_first"] and len(lines) > 1:
        lines[0] = "<b>" + lines[0] + "</b>"
    return html.escape("<br>".join(lines if n["shape"] != "lane" else [n["text"]]), quote=True)


def to_xml():
    out = ['<mxfile host="app.diagrams.net" version="24.0.0">']
    for pi, p in enumerate(pages):
        out.append(f'  <diagram id="p{pi+1}" name="{html.escape(p["name"])}">')
        out.append(f'    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{p["w"]}" pageHeight="{p["h"]}" math="0" shadow="0">')
        out.append('      <root><mxCell id="0"/><mxCell id="1" parent="0"/>')
        order = [n for n in p["nodes"] if n["shape"] == "lane"] + [n for n in p["nodes"] if n["shape"] != "lane"]
        for n in order:
            out.append(f'        <mxCell id="p{pi}_{n["id"]}" value="{value(n)}" style="{html.escape(style(n), quote=True)}" vertex="1" parent="1">'
                       f'<mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" as="geometry"/></mxCell>')
        for ei, e in enumerate(p["edges"]):
            st = f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeWidth=1.5;strokeColor={EDGE[e['color']]};fontSize=11;fontColor={EDGE[e['color']]};"
            if e["dashed"]:
                st += "dashed=1;"
            if e["exit"]:
                st += f"exitX={e['exit'][0]};exitY={e['exit'][1]};exitDx=0;exitDy=0;"
            if e["entry"]:
                st += f"entryX={e['entry'][0]};entryY={e['entry'][1]};entryDx=0;entryDy=0;"
            geo = '<mxGeometry relative="1" as="geometry"/>'
            if e["via"]:
                pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in e["via"])
                geo = f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
            out.append(f'        <mxCell id="p{pi}_e{ei}" value="{html.escape(e["label"])}" style="{html.escape(st, quote=True)}" edge="1" parent="1" source="p{pi}_{e["src"]}" target="p{pi}_{e["dst"]}">{geo}</mxCell>')
        out.append('      </root>')
        out.append('    </mxGraphModel>')
        out.append('  </diagram>')
    out.append('</mxfile>')
    return "\n".join(out) + "\n"


# ====================================================================== preview (same geometry)
def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
    os.makedirs(PREVIEW, exist_ok=True)
    paths = []
    for pi, p in enumerate(pages):
        fig, ax = plt.subplots(figsize=(p["w"] / 100, p["h"] / 100))
        ax.set_xlim(0, p["w"]); ax.set_ylim(p["h"], 0); ax.axis("off")
        nodes = {n["id"]: n for n in p["nodes"]}
        for n in [n for n in p["nodes"] if n["shape"] == "lane"] + [n for n in p["nodes"] if n["shape"] != "lane"]:
            f, s = COL[n["kind"]]
            x, y, w, h = n["x"], n["y"], n["w"], n["h"]
            if n["shape"] == "text":
                import textwrap
                ax.text(x, y + h / 2, textwrap.fill(n["text"], max(20, int(w / (n["fs"] * .6)))), fontsize=n["fs"] * .75, fontweight="bold" if n["fs"] > 12 else "normal", va="center", ha="left"); continue
            if n["shape"] == "lane":
                ax.add_patch(plt.Rectangle((x, y), w, h, fc=f, ec=s, lw=1)); ax.text(x + 12, y + 14, n["text"], fontsize=9, fontweight="bold", va="center", color="#4a4a68"); continue
            if n["shape"] == "diamond":
                ax.add_patch(Polygon([(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)], fc=f, ec=s, lw=1.5))
            else:
                ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=8", fc=f, ec=s, lw=1.5))
            lines = n["text"].split("\n")
            ax.text(x + w / 2, y + h / 2, "\n".join(lines), fontsize=n["fs"] * .62, ha="center", va="center", color="white" if n["kind"] == "start" else "#1f2933", linespacing=1.25)
        for e in p["edges"]:
            pts = route(p, e, nodes)
            col = EDGE[e["color"]]
            for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:-1] and pts[1:]):
                pass
            xs, ys = zip(*pts)
            if len(pts) > 2:
                ax.plot(xs[:-1], ys[:-1], color=col, lw=1.5, ls="--" if e["dashed"] else "-")
            ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=11, lw=1.5, color=col, linestyle="--" if e["dashed"] else "-"))
            if e["label"]:
                mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
                ax.text(mx + 4, my - 4, e["label"], fontsize=7.5, color=col)
        path = os.path.join(PREVIEW, f"drawio_page{pi+1}.png")
        fig.savefig(path, dpi=100, bbox_inches="tight", facecolor="white"); plt.close(fig); paths.append(path)
    return paths


if __name__ == "__main__":
    problems = {p["name"]: check_overlaps(p) for p in pages}
    for k, v in problems.items():
        print(("OK   " if not v else "PROBLEM ") + k, v if v else "")
    open(os.path.join(HERE, "architecture.drawio"), "w", encoding="utf-8").write(to_xml())
    print("wrote docs/architecture.drawio")
    for pth in preview():
        print("preview", pth)
    sys.exit(1 if any(problems.values()) else 0)
