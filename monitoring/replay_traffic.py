"""
Send validation tickets to a running API so the Grafana dashboard has data to show.
The dashboard reads the API's in-memory Prometheus counters, so it is empty until tickets are processed,
and it resets whenever the API restarts. Rate and 'increase' panels need traffic over several scrapes (15 s apart).

  uvicorn src.api:app --port 8000                       (one terminal)
  python monitoring/replay_traffic.py --n 60 --rounds 5 (another: 5 rounds, pausing between them)
"""
import argparse
import json
import os
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("ticket_id", "channel", "subject", "body", "customer_id", "customer_name", "customer_tier", "customer_region", "language_fluency")


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))


ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://localhost:8000")
ap.add_argument("--n", type=int, default=60, help="tickets per round")
ap.add_argument("--delay", type=float, default=0.5, help="seconds between tickets")
ap.add_argument("--rounds", type=int, default=1, help="repeat the set this many times")
ap.add_argument("--pause", type=float, default=20.0, help="seconds between rounds (give Prometheus time to scrape)")
a = ap.parse_args()
tickets = json.load(open(os.path.join(ROOT, "data", "validation_tickets.json")))[: a.n]
for rnd in range(a.rounds):
    for t in tickets:
        r = post(a.url + "/tickets", {k: t[k] for k in KEYS})
        print(f"round {rnd + 1}/{a.rounds} {t['ticket_id']} {r['decision']} {r['reason_code']} {r['latency_ms']} ms", flush=True)
        time.sleep(a.delay)
    if rnd + 1 < a.rounds:
        # a human correction now and then, so the feedback panel has something to show
        post(a.url + "/feedback", {"ticket_id": tickets[rnd]["ticket_id"], "corrected_route": "escalate", "note": "demo"})
        time.sleep(a.pause)
