"""
What distinguishes tickets labelled 'escalate' from 'auto_respond' once the four safety intents are removed?
Looks at answerability, tier, channel, fluency, urgency, and the text itself.
Run: venv/bin/python3 evaluation/analyze_escalations.py
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAFETY = {"security_incident", "compliance_request", "feature_request", "unclear_request"}
dev = json.load(open("data/development_tickets.json"))
rest = [t for t in dev if t["labels"]["intent"] not in SAFETY]
esc = [t for t in rest if t["labels"]["expected_route"] == "escalate"]
auto = [t for t in rest if t["labels"]["expected_route"] == "auto_respond"]
print(f"non-safety: {len(rest)}  escalate={len(esc)}  auto={len(auto)}")
print("escalate answerable:", Counter(t["labels"]["answerable_from_docs"] for t in esc))
for field in ("customer_tier", "channel", "language_fluency"):
    e, a = Counter(t[field] for t in esc), Counter(t[field] for t in auto)
    print(field, {k: f"esc {e[k]/len(esc):.2f} vs auto {a[k]/len(auto):.2f}" for k in sorted(set(e) | set(a))})
print("urgency", {k: f"esc {Counter(t['labels']['urgency'] for t in esc)[k]/len(esc):.2f} vs auto {Counter(t['labels']['urgency'] for t in auto)[k]/len(auto):.2f}" for k in ("high", "medium", "low")})
print("\nintents with highest escalate share (non-safety):")
ic = Counter(t["labels"]["intent"] for t in rest)
ie = Counter(t["labels"]["intent"] for t in esc)
for k, v in sorted(ie.items(), key=lambda kv: -kv[1] / ic[kv[0]])[:8]:
    print(f"  {k:26} {v}/{ic[k]}")
print("\nSAMPLE escalate+answerable:")
for t in [x for x in esc if x["labels"]["answerable_from_docs"]][:7]:
    print(" -", t["labels"]["intent"], "|", t["body"][:170].replace("\n", " "))
print("\nSAMPLE escalate+NOT answerable:")
for t in [x for x in esc if not x["labels"]["answerable_from_docs"]][:7]:
    print(" -", t["labels"]["intent"], "|", t["body"][:170].replace("\n", " "))
print("\nSAMPLE auto_respond (same intents):")
for t in auto[:5]:
    print(" -", t["labels"]["intent"], "|", t["body"][:170].replace("\n", " "))
# do escalate tickets mention certain words more often?
words = lambda ts: Counter(w for t in ts for w in set(re.findall(r"[a-z]{4,}", (t["subject"] + " " + t["body"]).lower())))
we, wa = words(esc), words(auto)
dist = sorted(((we[w] / len(esc) - wa[w] / len(auto), w) for w in set(we) | set(wa) if we[w] >= 5), reverse=True)[:14]
print("\nwords over-represented in escalations:", [(w, round(d, 2)) for d, w in dist])
