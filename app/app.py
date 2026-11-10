"""Local web app: explore the gold cost of TFT upgrades under competition.

Run from the repository root:   python app/app.py
Then open http://127.0.0.1:5000 in a browser.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from flask import Flask, jsonify, render_template, request

from tftcost import H, NEED, ODDS, expected_gold, expected_shops, simulate_gold

app = Flask(__name__)
BUDGETS = [50, 100, 150, 200, 300]


def _num(name, default, lo, hi, cast=int):
    raw = request.args.get(name)
    if raw in (None, ""):
        return default
    try:
        value = cast(raw)
    except ValueError:
        raise ValueError(f"{name} must be a number")
    if not lo <= value <= hi:
        raise ValueError(f"{name} must be between {lo} and {hi}")
    return value


@app.get("/")
def index():
    return render_template("index.html", odds=ODDS, h=H, need=NEED)


@app.get("/api/cost")
def cost():
    try:
        cost_tier = _num("cost", 3, 1, 5)
        level = _num("level", 7, 1, 10)
        star = _num("star", 3, 2, 3)
        competitors = _num("competitors", 0, 0, 5)
        owned = _num("owned", 0, 0, NEED[star] - 1)
        h = _num("h", None, 0.0, 10.0, float)
    except ValueError as err:
        return jsonify(error=str(err)), 400

    odds = ODDS[level][cost_tier - 1]
    out = {"cost": cost_tier, "level": level, "star": star, "competitors": competitors,
           "owned": owned, "h": H[cost_tier] if h is None else h, "odds": odds}
    g = simulate_gold(level, cost_tier, star, competitors, owned, h)
    out["feasible"] = bool(np.isfinite(g).all())
    out["by_competitors"] = [
        None if np.isinf(v) else round(v, 1)
        for v in (expected_gold(level, cost_tier, star, c, owned, h) for c in range(6))
    ]
    if not out["feasible"]:
        out["reason"] = (f"The shop never shows {cost_tier}-cost units at level {level}." if odds == 0
                         else "The pool cannot supply enough copies once the competitors hold theirs.")
        return jsonify(out)

    out["expected_gold"] = round(expected_gold(level, cost_tier, star, competitors, owned, h), 1)
    out["expected_shops"] = round(expected_shops(level, cost_tier, star, competitors, owned, h), 1)
    out["median"] = round(float(np.median(g)), 1)
    out["p90"] = round(float(np.quantile(g, 0.9)), 1)
    out["p_within"] = {str(b): round(float((g <= b).mean()), 3) for b in BUDGETS}
    top = float(np.quantile(g, 0.995))
    grid = np.linspace(0, top, 80)
    s = np.sort(g)
    out["curve"] = [[round(float(b), 1), round(float(np.searchsorted(s, b, side="right") / len(s)), 4)]
                    for b in grid]
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
