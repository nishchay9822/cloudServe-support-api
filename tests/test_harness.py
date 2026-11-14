"""A9, A10: the harness takes any input/output path, finishes unattended and writes its own report."""
import json
import os
import subprocess
import sys

from tests.conftest import ROOT

HARNESS = os.path.join(ROOT, "evaluation", "harness.py")
VAL = os.path.join(ROOT, "data", "validation_tickets.json")


def run(args, tmp_path, key=""):
    env = {**os.environ, "OPENROUTER_API_KEY": key, "LLM_API_KEY": key, "DATABASE_URL": f"sqlite:///{tmp_path}/d.db", "ANONYMIZED_TELEMETRY": "False"}
    return subprocess.run([sys.executable, HARNESS, *args], capture_output=True, text=True, cwd=ROOT, env=env, timeout=600)


def test_both_paths_are_required(tmp_path):
    assert run(["--output", str(tmp_path / "o.json")], tmp_path).returncode != 0
    assert run(["--input", VAL], tmp_path).returncode != 0


def test_missing_input_file_exits_2_without_traceback(tmp_path):
    p = run(["--input", str(tmp_path / "nope.json"), "--output", str(tmp_path / "o.json")], tmp_path)
    assert p.returncode == 2 and "Traceback" not in p.stderr


def test_runs_over_an_unseen_file_and_writes_json_and_report(tmp_path):
    src = json.load(open(VAL))[:8]
    inp = tmp_path / "hidden_like.json"
    inp.write_text(json.dumps(src))
    out = tmp_path / "sub" / "dir" / "result.json"       # output directory does not exist yet
    p = run(["--input", str(inp), "--output", str(out)], tmp_path)
    assert p.returncode == 0, p.stderr
    d = json.load(open(out))
    assert len(d["results"]) == 8 and d["metrics"]["governance"]["log_reconciles"] is True
    assert d["metrics"]["governance"]["decisions_logged"] == 8
    assert os.path.exists(str(out)[:-5] + ".md")        # A10: report produced automatically


def test_unlabelled_tickets_are_processed_too(tmp_path):
    src = [{k: v for k, v in t.items() if k not in ("labels", "history")} for t in json.load(open(VAL))[:5]]
    inp = tmp_path / "u.json"
    inp.write_text(json.dumps(src))
    p = run(["--input", str(inp), "--output", str(tmp_path / "o.json")], tmp_path)
    d = json.load(open(tmp_path / "o.json"))
    assert p.returncode == 0 and len(d["results"]) == 5 and d["metrics"]["run"]["labelled"] is False


def test_bad_tickets_do_not_stop_the_run(tmp_path):
    mixed = json.load(open(VAL))[:3] + [None, "junk", {"ticket_id": "ONLY-ID"}, {"channel": "pigeon"}] + json.load(open(VAL))[3:5]
    inp = tmp_path / "m.json"
    inp.write_text(json.dumps(mixed))
    p = run(["--input", str(inp), "--output", str(tmp_path / "o.json")], tmp_path)
    d = json.load(open(tmp_path / "o.json"))
    assert p.returncode == 0 and len(d["results"]) == len(mixed)
    assert d["metrics"]["governance"]["log_reconciles"] is True
