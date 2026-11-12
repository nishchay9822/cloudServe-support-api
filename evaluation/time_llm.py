"""Compare model latency with default provider routing vs OpenRouter provider sorting.
Run: venv/bin/python3 evaluation/time_llm.py"""
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import llm  # noqa: E402

msgs = [{"role": "system", "content": "You write short support replies."},
        {"role": "user", "content": "Explain in 4 sentences how to roll back a failed deployment to the previous revision."}]


def run(label, extra):
    ts = []
    for _ in range(6):
        s = time.time()
        resp = llm._client().chat.completions.create(model=llm.model_name(), messages=msgs, max_tokens=160,
                                                     temperature=0, extra_body=extra)
        ts.append(time.time() - s)
    print(f"{label:28} median={statistics.median(ts):.1f}s max={max(ts):.1f}s all=" + ", ".join(f"{x:.1f}" for x in ts))


run("default routing", {})
run("provider sort=latency", {"provider": {"sort": "latency"}})
run("provider sort=throughput", {"provider": {"sort": "throughput"}})
