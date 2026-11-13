"""Generate every report figure from evaluation/results and data/. Run via build_report.py."""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RES = os.path.join(ROOT, "evaluation", "results")
OUT = os.path.join(HERE, "fig")
os.makedirs(OUT, exist_ok=True)
NAVY, GREEN, AMBER, RED, GREY, PURPLE = "#1f4e79", "#4c9a6a", "#d9a441", "#c0504d", "#8a97a6", "#7d5ba6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def J(name):
    return json.load(open(os.path.join(RES, name)))


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def box(ax, x, y, w, h, text, fc, ec=None, fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec or fc, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", color="#1f2933")


def arrow(ax, p, q, color="#1f2933", style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=9, lw=1, color=color, linestyle=ls, connectionstyle=f"arc3,rad={rad}"))


def fig_architecture():
    fig, ax = plt.subplots(figsize=(11, 5.4))
    ax.set_xlim(0, 23.4); ax.set_ylim(0, 10.6); ax.axis("off")
    for i, c in enumerate(["email", "chat", "docs_comment", "forum"]):
        box(ax, 0.2, 7.9 - i * 1.5, 2.8, 1.0, c, "#dae8fc", "#6c8ebf", fs=8)
    box(ax, 3.7, 4.7, 2.1, 1.6, "Kill switch\non?", "#f8cecc", "#b85450", bold=True, fs=8)
    for i in range(4):
        arrow(ax, (3.0, 8.4 - i * 1.5), (3.7, 5.5), color=GREY)
    W, X0, STEP = 2.45, 6.4, 2.85
    steps = ["1 Ingest\nnormalise +\ninjection screen", "2 Classify\nkNN first,\nLLM if unsure", "3 Retrieve\nChroma search,\nmin score 0.30",
             "4 Route\ndeterministic\ncode", "5 Generate\nfull article,\ncited", "6 Validate\nPII, grounding,\nfigures, tone"]
    cols = [GREEN, GREEN, GREEN, "#f3e3a8", GREEN, "#f3e3a8"]
    xs = [X0 + i * STEP for i in range(6)]
    for t, x, fc in zip(steps, xs, cols):
        box(ax, x, 4.5, W, 2.0, t, fc, "#5b6b7b", fs=7.2)
    arrow(ax, (5.8, 5.5), (X0, 5.5)); ax.text(6.15, 5.75, "off", fontsize=7, ha="center")
    ax.add_patch(FancyBboxPatch((X0 - 0.2, 4.3), 6 * STEP - 0.4, 2.4, boxstyle="round,pad=0.02,rounding_size=0.1", fc="none", ec="#8a97a6", lw=1, ls="--"))
    ax.text(X0, 6.78, "LangGraph state machine (src/pipeline.py): conditional edges send any escalation straight to the end", fontsize=6.8, color="#5b6b7b", style="italic")
    for a_, b_ in zip(xs, xs[1:]):
        arrow(ax, (a_ + W, 5.5), (b_, 5.5))
    box(ax, 14.0, 1.3, 4.6, 1.3, "Escalate to human\nsummary + sources + reason", "#f8cecc", "#b85450", fs=7.4)
    box(ax, 20.2, 1.3, 2.9, 1.3, "Auto reply\n(cited)", "#cfe8d5", "#4c9a6a", fs=7.4)
    arrow(ax, (xs[5] + W * 0.75, 4.5), (21.65, 2.6), color=GREEN); ax.text(22.0, 3.3, "all pass", fontsize=7, color=GREEN)
    arrow(ax, (xs[5] + W * 0.25, 4.5), (17.5, 2.6), color=RED); ax.text(18.3, 3.0, "blocked / NO_ANSWER", fontsize=7, color=RED)
    arrow(ax, (xs[3] + W * 0.5, 4.5), (15.2, 2.6), color=RED); ax.text(15.6, 3.3, "safety, no evidence,\nlow confidence", fontsize=7, color=RED, ha="left")
    arrow(ax, (4.75, 4.7), (14.0, 1.7), color=RED, rad=0.25); ax.text(3.0, 3.2, "switch on: every\nticket to a human", fontsize=7, color=RED)
    box(ax, 7.2, 8.7, 6.9, 1.3, "LLM provider (OpenRouter / any OpenAI-compatible)\nretries, circuit breaker, fail fast on 401/402", "#e1d5e7", "#7d5ba6", fs=7)
    arrow(ax, (xs[1] + W / 2, 6.5), (9.6, 8.7), color=PURPLE, style="<|-|>", ls="--")
    arrow(ax, (xs[4] + W / 2, 6.5), (13.0, 8.7), color=PURPLE, style="<|-|>", ls="--")
    box(ax, 6.6, 0.1, 5.2, 1.0, "Chroma: articles (hybrid dense + BM25)\n+ labelled-ticket neighbours", "#e1d5e7", "#7d5ba6", fs=7.4)
    arrow(ax, (xs[1] + 0.6, 4.5), (8.0, 1.1), color=PURPLE, style="<|-|>", ls="--")
    arrow(ax, (xs[2] + 0.6, 4.5), (10.2, 1.1), color=PURPLE, style="<|-|>", ls="--")
    box(ax, 12.2, 0.1, 3.4, 1.0, "SQLite decision log\n+ resolution records", "#e1d5e7", "#7d5ba6", fs=7.2)
    arrow(ax, (xs[3] + W * 0.3, 4.5), (13.6, 1.1), color=PURPLE, ls="--")
    box(ax, 0.2, 0.1, 5.8, 1.0, "FastAPI: /tickets /feedback /decisions\n/health /metrics /admin/kill-switch", "#dae8fc", "#6c8ebf", fs=7.2)
    box(ax, 16.2, 0.1, 6.9, 1.0, "Feedback loop: POST /feedback\nhuman corrections → log + neighbour index", "#fde9d9", "#e8660b", fs=7.2)
    arrow(ax, (16.2, 0.6), (15.6, 0.6), color="#e8660b")
    box(ax, 17.6, 8.8, 5.2, 1.1, "Prometheus /metrics → Grafana", "#eeeeee", "#8a97a6", fs=7.4)
    arrow(ax, (xs[5] + W * 0.6, 6.5), (20.5, 8.8), color=GREY, ls="--")
    return save(fig, "architecture_fig2.png")


def fig_discovery():
    t = json.load(open(os.path.join(ROOT, "data", "development_tickets.json")))
    n = len(t)
    share = lambda f: sum(1 for x in t if f(x)) / n * 100
    base = {"Answerable from\ndocs": share(lambda x: x["labels"]["answerable_from_docs"]), "Escalated": share(lambda x: x["history"]["escalated"]),
            "First-contact\nresolved": share(lambda x: x["history"]["first_contact_resolution"]), "Repeat\ncontact": share(lambda x: x["history"]["repeat_contact"]),
            "Must not\nauto-respond": share(lambda x: x["labels"]["must_not_auto_respond"])}
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.2), gridspec_kw={"width_ratios": [1.5, 1]})
    cols = [GREEN, RED, NAVY, AMBER, GREY]
    bars = a.bar(list(base), list(base.values()), color=cols)
    for r, v in zip(bars, base.values()):
        a.text(r.get_x() + r.get_width() / 2, v + 1.2, f"{v:.1f}%", ha="center", fontsize=8)
    a.set_ylim(0, 85); a.set_ylabel("% of 500 development tickets"); a.set_title("(a) What the ticket data says", fontsize=9)
    tiers = ["enterprise", "business", "standard"]
    fcr = [sum(1 for x in t if x["customer_tier"] == k and x["history"]["first_contact_resolution"]) / sum(1 for x in t if x["customer_tier"] == k) * 100 for k in tiers]
    bars = b.bar(tiers, fcr, color=[RED, GREEN, AMBER])
    for r, v in zip(bars, fcr):
        b.text(r.get_x() + r.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontsize=8)
    b.set_ylim(0, 60); b.set_ylabel("First-contact resolution, %"); b.set_title("(b) Enterprise resolves worst", fontsize=9)
    fig.tight_layout()
    return save(fig, "discovery.png")


def fig_signals():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.2))
    names = ["Retrieval score", "LLM answerability\njudge"]
    dev, val = [0.505, 0.46], [0.468, 0.42]
    x = range(2)
    a.bar([i - 0.2 for i in x], dev, 0.4, color=NAVY, label="dev (n=500)")
    a.bar([i + 0.2 for i in x], val, 0.4, color=AMBER, label="validation (n=80)")
    a.axhline(0.5, color=RED, ls="--", lw=1); a.text(1.55, 0.512, "chance", color=RED, fontsize=8, ha="right")
    a.set_xticks(list(x)); a.set_xticklabels(names); a.set_ylim(0.3, 0.7); a.set_ylabel("AUC for 'should escalate'")
    a.legend(fontsize=7.5, loc="upper right"); a.set_title("(a) Signals tried for non-safety tickets", fontsize=9)
    labs = ["Route label", "Urgency label"]; vals = [87.8, 68.5]
    bars = b.bar(labs, vals, color=[NAVY, AMBER])
    for r, v in zip(bars, vals):
        b.text(r.get_x() + r.get_width() / 2, v + 1.5, f"{v}%", ha="center", fontsize=8)
    b.set_ylim(0, 105); b.set_ylabel("% of identical-text pairs that agree"); b.set_title("(b) Same text, same label?", fontsize=9)
    fig.tight_layout()
    return save(fig, "signals.png")


def fig_outcomes():
    dev, val = J("dev_run.json")["metrics"], J("gate_run_validation.json")["metrics"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    groups = [("Development\n(n=500)", dev, 0.372), ("Validation\n(n=80)", val, 0.4125)]
    esc = [("Baseline\nescalation", [dev["business"]["baseline_escalation_rate"], val["business"]["baseline_escalation_rate"]], GREY),
           ("System\nescalation", [dev["business"]["system_escalation_rate"], val["business"]["system_escalation_rate"]], GREEN),
           ("Adjusted\n(see text)", [0.372, 0.4125], AMBER)]
    w = 0.26
    for i, (lab, v, c) in enumerate(esc):
        bars = axs[0].bar([j + (i - 1) * w for j in range(2)], [x * 100 for x in v], w, color=c, label=lab.replace("\n", " "))
        for r, x in zip(bars, v):
            axs[0].text(r.get_x() + r.get_width() / 2, x * 100 + 1, f"{x*100:.0f}", ha="center", fontsize=7.5)
    axs[0].axhline(30, color=RED, ls="--", lw=1); axs[0].text(1.45, 31, "target 30%", color=RED, fontsize=7.5, ha="right")
    axs[0].set_xticks(range(2)); axs[0].set_xticklabels([g[0] for g in groups]); axs[0].set_ylim(0, 70)
    axs[0].set_ylabel("% of tickets"); axs[0].legend(fontsize=7, loc="upper right", ncol=1); axs[0].set_title("(a) Escalation rate", fontsize=9)
    fcr = [("Baseline\nFCR", [dev["business"]["baseline_fcr"], val["business"]["baseline_fcr"]], GREY),
           ("Auto-resolution\nproxy", [dev["business"]["auto_resolution_proxy"], val["business"]["auto_resolution_proxy"]], GREEN)]
    for i, (lab, v, c) in enumerate(fcr):
        bars = axs[1].bar([j + (i - 0.5) * 0.34 for j in range(2)], [x * 100 for x in v], 0.34, color=c, label=lab.replace("\n", " "))
        for r, x in zip(bars, v):
            axs[1].text(r.get_x() + r.get_width() / 2, x * 100 + 1, f"{x*100:.1f}", ha="center", fontsize=7.5)
    axs[1].axhline(60, color=RED, ls="--", lw=1); axs[1].text(-0.45, 61.5, "target 60%", color=RED, fontsize=7.5, ha="left")
    axs[1].set_xticks(range(2)); axs[1].set_xticklabels([g[0] for g in groups]); axs[1].set_ylim(0, 80)
    axs[1].legend(fontsize=7, loc="upper right"); axs[1].set_title("(b) First-contact resolution (proxy)", fontsize=9)
    fig.tight_layout()
    return save(fig, "outcomes.png")


def fig_latency():
    orv = J("gate_run_validation.json")["metrics"]["latency"]
    grq = J("gate_run_validation_groq.json")["metrics"]["latency"]
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    labels = ["OpenRouter\n(paid)", "Groq\n(free tier)"]
    p50 = [orv["auto_p50_ms"] / 1000, grq["auto_p50_ms"] / 1000]; p95 = [orv["auto_p95_ms"] / 1000, grq["auto_p95_ms"] / 1000]
    b1 = ax.bar([i - 0.18 for i in range(2)], p50, 0.36, color=GREEN, label="p50")
    b2 = ax.bar([i + 0.18 for i in range(2)], p95, 0.36, color=NAVY, label="p95")
    for r, v in list(zip(b1, p50)) + list(zip(b2, p95)):
        ax.text(r.get_x() + r.get_width() / 2, v + 0.2, f"{v:.2f}s", ha="center", fontsize=8)
    ax.axhline(3, color=RED, ls="--", lw=1); ax.text(1.5, 3.15, "target p95 < 3 s", color=RED, fontsize=8, ha="right")
    ax.set_xticks(range(2)); ax.set_xticklabels(labels); ax.set_ylabel("Auto-reply latency, seconds"); ax.legend(fontsize=8, loc="upper left")
    ax.set_ylim(0, 13)
    return save(fig, "latency.png")


def fig_fairness():
    d = J("fairness_dev.json")["segments"]
    rows = []
    for dim in ("customer_tier", "language_fluency", "ticket_length", "region", "channel"):
        for g, s in d[dim]["groups"].items():
            rows.append((f"{dim.replace('customer_', '').replace('language_', '').replace('ticket_', '')}: {g.split(' (')[0]}", s["route_accuracy"], s["route_ci95"]))
    rows = rows[::-1]
    overall = J("dev_run.json")["metrics"]["routing"]["route_accuracy"]
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    for i, (lab, v, ci) in enumerate(rows):
        ax.plot(ci, [i, i], color=NAVY, lw=2); ax.plot([v], [i], "o", color=NAVY, ms=4.5)
    ax.axvline(overall, color=RED, ls="--", lw=1); ax.text(overall + 0.003, len(rows) - 0.4, f"overall {overall*100:.0f}%", color=RED, fontsize=7.5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.set_xlabel("Route accuracy with 95% interval (500 development tickets)"); ax.set_xlim(0.55, 0.92)
    return save(fig, "fairness.png")


def fig_risk():
    pos = {"R-01": ("Medium", "Very high"), "R-02": ("Low", "Very high"), "R-03": ("Low", "Very high"), "R-04": ("Medium", "High"),
           "R-05": ("High", "High"), "R-06": ("High", "Medium"), "R-07": ("Medium", "Medium"), "R-08": ("Low", "Low"),
           "R-09": ("High", "High"), "R-10": ("Medium", "High"), "R-11": ("High", "High"), "R-12": ("Low", "Medium")}
    L, I = ["Low", "Medium", "High"], ["Low", "Medium", "High", "Very high"]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for li, l in enumerate(L):
        for ii, i in enumerate(I):
            score = (li + 1) * (ii + 1)
            ax.add_patch(plt.Rectangle((li, ii), 1, 1, fc="#cfe8d5" if score <= 3 else ("#f3e3a8" if score <= 6 else "#f1c0bd"), ec="white", lw=2))
    cells = {}
    for k, (l, i) in pos.items():
        cells.setdefault((L.index(l), I.index(i)), []).append(k)
    for (li, ii), ks in cells.items():
        ax.text(li + 0.5, ii + 0.5, "\n".join(", ".join(ks[j:j + 2]) for j in range(0, len(ks), 2)), ha="center", va="center", fontsize=8, fontweight="bold")
    ax.set_xlim(0, 3); ax.set_ylim(0, 4); ax.set_xticks([0.5, 1.5, 2.5]); ax.set_xticklabels(L); ax.set_yticks([0.5, 1.5, 2.5, 3.5]); ax.set_yticklabels(I)
    ax.set_xlabel("Likelihood (with mitigations in place)"); ax.set_ylabel("Impact"); ax.spines[:].set_visible(False)
    return save(fig, "risk.png")


def make_all():
    return {"arch": fig_architecture(), "disc": fig_discovery(), "signals": fig_signals(), "outcomes": fig_outcomes(),
            "latency": fig_latency(), "fair": fig_fairness(), "risk": fig_risk()}


if __name__ == "__main__":
    print(make_all())
