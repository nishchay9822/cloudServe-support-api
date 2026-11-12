"""
Send validation tickets to a running API so the dashboard has data to show.
  uvicorn src.api:app --port 8000      (in one terminal)
  python monitoring/replay_traffic.py --n 60 --delay 0.5
"""
import argparse, json, os, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("ticket_id", "channel", "subject", "body", "customer_id", "customer_name", "customer_tier", "customer_region", "language_fluency")
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://localhost:8000"); ap.add_argument("--n", type=int, default=60); ap.add_argument("--delay", type=float, default=0.5)
a = ap.parse_args()
for t in json.load(open(os.path.join(ROOT, "data", "validation_tickets.json")))[: a.n]:
    req = urllib.request.Request(a.url + "/process", data=json.dumps({k: t[k] for k in KEYS}).encode(), headers={"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    print(t["ticket_id"], r["decision"], r["reason_code"], f'{r["latency_ms"]} ms')
    time.sleep(a.delay)
