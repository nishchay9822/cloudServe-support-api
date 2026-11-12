"""
Prompt loader. Prompts live in prompts/ as versioned text files (Stage 3 library).
Files hold a [SYSTEM] block and a [USER] block; '#' lines at the top are metadata.
Placeholders look like {name} and are filled with plain string replacement,
so JSON braces inside a prompt never need escaping.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_prompt(relative_path: str) -> tuple:
    """Return (system_text, user_template) from a prompt file."""
    path = os.path.join(ROOT, relative_path)
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if not ln.startswith("#")]
    text = "\n".join(lines)
    m = re.search(r"\[SYSTEM\](.*?)\[USER\](.*)", text, flags=re.S)
    if not m:
        raise ValueError(f"{relative_path} must contain [SYSTEM] and [USER] blocks")
    return m.group(1).strip(), m.group(2).strip()


def render(template: str, **values) -> str:
    out = template
    for key, val in values.items():
        out = out.replace("{" + key + "}", str(val))
    return out
