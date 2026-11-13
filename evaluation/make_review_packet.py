"""
Build the packet a human second assessor needs (NFR-03: hallucination assessed by two independent assessors).

  evaluation/results/human_review_packet.html    read this: for each reply, the customer's ticket, the reply, and the FULL text of every
                                                 article it cites. The model judge's verdict is deliberately NOT shown (blind review).
  evaluation/results/human_review_answers.csv    fill this in: ticket_id, human_hallucination (Y or N), human_notes

A reply HALLUCINATES if it states anything (a step, a number, a version, a duration, a limit, a feature) that is not supported by the cited
articles or by the customer's own message. Missing a step is not hallucination. A wrong citation is not hallucination unless it carries an
unsupported claim.

  venv/bin/python3 evaluation/make_review_packet.py [--run evaluation/results/gate_run_validation.json] [--n 50]
Then, after filling the CSV:   venv/bin/python3 evaluation/review_agreement.py
"""
import argparse
import csv
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--run", default=os.path.join(ROOT, "evaluation", "results", "gate_run_validation.json"))
ap.add_argument("--tickets", default=os.path.join(ROOT, "data", "validation_tickets.json"))
ap.add_argument("--n", type=int, default=50)
a = ap.parse_args()
run = json.load(open(a.run))
verdict_ids = list((run["metrics"].get("judge") or {}).get("verdicts", {}).keys())
tickets = {t["ticket_id"]: t for t in json.load(open(a.tickets))}
articles = {d["doc_id"]: d for d in json.load(open(os.path.join(ROOT, "data", "documentation.json")))}
by = {r["ticket_id"]: r for r in run["results"]}
# the same replies the model judge assessed, so the two assessors are comparable
ids = [i for i in (verdict_ids or [r["ticket_id"] for r in run["results"] if r["decision"] == "auto_respond"]) if i in by][: a.n]

out = ["<!doctype html><meta charset='utf-8'><title>Reply review packet</title>",
       "<style>body{font-family:Georgia,serif;max-width:900px;margin:2em auto;line-height:1.45;color:#1f2933}h2{border-top:3px solid #1f4e79;padding-top:.6em;color:#1f4e79}"
       ".box{background:#f4f7fa;border-left:4px solid #6c8ebf;padding:.6em 1em;margin:.6em 0;white-space:pre-wrap}.reply{border-left-color:#82b366;background:#f1f8f1}"
       ".art{border-left-color:#9673a6;background:#f7f2fa;font-size:.9em}small{color:#666}</style>",
       "<h1>Reply review packet</h1>",
       f"<p>{len(ids)} automatic replies. For each one decide: <b>does the reply state anything that the cited articles or the customer's message do not support?</b> "
       "Answer Y (hallucination) or N in <code>human_review_answers.csv</code>, with a short note when Y. Missing steps do not count; unsupported statements do.</p>"]
for i, tid in enumerate(ids, 1):
    r, t = by[tid], tickets.get(tid, {})
    out.append(f"<h2>{i}. {html.escape(tid)}</h2>")
    out.append(f"<div class='box'><b>Customer ticket</b> <small>({html.escape(str(t.get('channel')))})</small>\n{html.escape(((t.get('subject') or '') + chr(10) + (t.get('body') or '')).strip())}</div>")
    out.append(f"<div class='box reply'><b>Reply sent</b>\n{html.escape((r.get('response_text') or '').strip())}</div>")
    for c in r.get("citations", []):
        d = articles.get(c["doc_id"])
        if d:
            out.append(f"<div class='box art'><b>Cited article {html.escape(c['doc_id'])}: {html.escape(d['title'])}</b>\n{html.escape(d['content'])}</div>")
path = os.path.join(ROOT, "evaluation", "results", "human_review_packet.html")
open(path, "w", encoding="utf-8").write("\n".join(out))
csv_path = os.path.join(ROOT, "evaluation", "results", "human_review_answers.csv")
if not os.path.exists(csv_path):          # never overwrite answers someone has already entered
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticket_id", "human_hallucination (Y/N)", "human_notes"])
        for tid in ids:
            w.writerow([tid, "", ""])
print(f"packet: {path}  ({len(ids)} replies)\nanswers: {csv_path}")
