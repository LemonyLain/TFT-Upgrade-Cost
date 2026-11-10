"""Clean Jupyter notebooks and check them for private data before publishing.

    python scripts/clean_notebooks.py notebooks            # clear outputs in place
    python scripts/clean_notebooks.py notebooks --check    # only report problems

It clears all cell outputs and execution counts (outputs can contain player ids
and file paths), removes widget state, and reports:
  - ERROR  a string that looks like a Riot API key (RGAPI-...)
  - WARN   an absolute Windows path in code, e.g. D:/VS Code/data
  - WARN   the text puuid or summoner in code or outputs
The exit code is 1 if an error is found.
"""
import json
import re
import sys
from pathlib import Path

KEY = re.compile(r"RGAPI-[0-9A-Za-z-]{20,}")
WINPATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]")
PRIVATE = re.compile(r"puuid|summoner", re.I)


def text_of(cell):
    parts = ["".join(cell.get("source", []))]
    for out in cell.get("outputs", []):
        if "text" in out:
            parts.append("".join(out["text"]))
        for v in out.get("data", {}).values():
            parts.append("".join(v) if isinstance(v, list) else str(v))
    return "\n".join(parts)


def check(nb, name):
    errors, warns = [], []
    for i, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        full = text_of(cell)
        if KEY.search(full):
            errors.append(f"{name} cell {i}: looks like a Riot API key")
        if cell.get("cell_type") == "code" and WINPATH.search(src):
            warns.append(f"{name} cell {i}: absolute Windows path in code")
        if PRIVATE.search(full):
            where = "output" if PRIVATE.search(text_of({**cell, "source": []})) else "code"
            warns.append(f"{name} cell {i}: mentions puuid or summoner in {where}")
    return errors, warns


def clean(nb):
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    nb.get("metadata", {}).pop("widgets", None)
    return nb


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    only_check = "--check" in argv
    if not args:
        print(__doc__)
        return 2
    paths = sorted(Path(args[0]).rglob("*.ipynb"))
    if not paths:
        print("No notebooks found in", args[0])
        return 0
    bad = False
    for path in paths:
        nb = json.loads(path.read_text(encoding="utf-8"))
        errors, warns = check(nb, path.name)
        for line in errors:
            print("ERROR", line)
        for line in warns:
            print("WARN ", line)
        bad = bad or bool(errors)
        if not only_check:
            path.write_text(json.dumps(clean(nb), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print("cleaned", path)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
