"""
For identical ticket text, how consistent are the labels? Separates signal from label noise.
Run: venv/bin/python3 evaluation/analyze_label_consistency.py
"""
import json
import re
from collections import Counter, defaultdict

dev = json.load(open("data/development_tickets.json"))


def key(t):
    return re.sub(r"[^a-z]", "", (t["subject"] + t["body"]).lower())


groups = defaultdict(list)
for t in dev:
    groups[key(t)].append(t)
multi = [g for g in groups.values() if len(g) > 1]
print(f"{len(groups)} distinct texts across {len(dev)} tickets; {len(multi)} texts appear more than once ({sum(len(g) for g in multi)} tickets)")


def purity(field):
    pure = tot = 0
    for g in multi:
        c = Counter(field(t) for t in g)
        pure += c.most_common(1)[0][1]
        tot += len(g)
    return pure / tot


print(f"label purity within identical text:  intent={purity(lambda t: t['labels']['intent']):.3f}  "
      f"expected_route={purity(lambda t: t['labels']['expected_route']):.3f}  "
      f"answerable={purity(lambda t: t['labels']['answerable_from_docs']):.3f}  "
      f"urgency={purity(lambda t: t['labels']['urgency']):.3f}  tier-independent")
# route given (intent, answerable)
c = Counter((t["labels"]["expected_route"], t["labels"]["answerable_from_docs"]) for t in dev)
print("route x answerable:", dict(c))
# is route a function of text template for non-safety intents?
SAFETY = {"security_incident", "compliance_request", "feature_request", "unclear_request"}
rest_groups = [g for g in multi if g[0]["labels"]["intent"] not in SAFETY]
mixed = [g for g in rest_groups if len({t["labels"]["expected_route"] for t in g}) > 1]
print(f"non-safety repeated texts: {len(rest_groups)}; with mixed route labels: {len(mixed)}")
for g in mixed[:3]:
    print("  MIXED:", g[0]["body"][:90], Counter((t["labels"]["expected_route"], t["labels"]["answerable_from_docs"], t["customer_tier"]) for t in g))
