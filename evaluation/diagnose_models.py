"""Probe candidate models once and print the real error, if any. Run: venv/bin/python3 evaluation/diagnose_models.py [model ...]"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import llm  # noqa: E402

models = sys.argv[1:] or ["meta-llama/llama-3.1-8b-instruct", "meta-llama/llama-3.1-8b-instruct:free",
                          "meta-llama/llama-3.3-70b-instruct:free", "openai/gpt-4o-mini"]
for model in models:
    s = time.time()
    try:
        r = llm._client().chat.completions.create(model=model, messages=[{"role": "user", "content": "Reply OK"}],
                                                  max_tokens=4, timeout=25)
        print(f"{model:44} OK {r.choices[0].message.content!r} {time.time() - s:.1f}s", flush=True)
    except Exception as e:
        print(f"{model:44} ERR status={getattr(e, 'status_code', None)} {str(e)[:150]} {time.time() - s:.1f}s", flush=True)
