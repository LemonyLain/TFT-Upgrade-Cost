# The cost of upgrading under contestation in Teamfight Tactics (Set 18)

When several players chase the same unit, fewer copies are left for everyone. This project
prices that in gold. It models the shop as an absorbing Markov chain over copies owned,
computes the expected cost exactly, and uses Monte Carlo simulation for the spread and for
the chance of finishing within a gold budget. Competitors' holdings are estimated from
7,995 final boards of NA Challenger matches.

## Headline results (3-cost unit at level 7)

| Competitors | 2-star, expected gold | 3-star, expected gold | 3-star within 200 gold |
| --- | --- | --- | --- |
| 0 | 42 | 153 | 0.87 |
| 1 | 50 | 196 | 0.58 |
| 2 | 64 | 299 | 0.15 |
| 3 | 92 | infeasible | 0.00 |

A 4-cost or 5-cost 3-star is infeasible with even one competitor, because those champions
have only 10 and 9 copies. These are model outputs under a static pool, a fixed level and
constant competitor holdings, not observed spending.

Paper: add the link or PDF here.

## Quick start (Windows PowerShell)

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    pytest -q                 # checks the model reproduces the paper's numbers
    python app\app.py         # then open http://127.0.0.1:5000

On macOS or Linux, use `source .venv/bin/activate` and `python app/app.py`.

## What is here

| Path | Contents |
| --- | --- |
| `tftcost/` | The cost model (pool, odds, chain, expected gold, simulation) |
| `app/` | Local web app: choose tier, level, star and competitors and see cost and budget odds |
| `tests/` | Tests that reproduce the paper's tables |
| `notebooks/` | The analysis notebooks (see `notebooks/README.md`) |
| `scripts/` | `clean_notebooks.py` clears outputs and checks for private data |
| `tables/`, `figures/` | Outputs written by the notebooks |
| `data/` | Not included (see `data/README.md`) |

## Parameters

`H` (copies per competitor: 3.76, 4.34, 3.44, 2.50, 1.86 for 1- to 5-costs) and `BG`
(background depletion) come from final boards. The shop odds and pool sizes are the Set 18
values, from community sources (NoxuTFT, TFT Ninja).

## Limitations

The pool is static (no returns when players are eliminated), each competitor holds a constant
number of copies estimated from final boards, the level is fixed during the chase, and the
costs are not validated against gold actually spent.

## Disclaimer

This project is not endorsed by Riot Games and does not reflect the views or opinions of Riot
Games or anyone officially involved in producing or managing Riot Games properties. Riot Games
and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

## License

MIT (see `LICENSE`).
