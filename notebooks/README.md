# Notebooks

Copy your final notebooks here and run them in this order. They need `data/units.csv`
and `data/boards.csv` (see `../data/README.md`) and `pip install -r requirements-analysis.txt`.

| Notebook | What it does | Paper section |
| --- | --- | --- |
| `02_comp_clustering.ipynb` | UMAP + HDBSCAN comp families, contestation counts | 3 |
| `03_board_value_xgboost_shap.ipynb` | Placement models and SHAP | 3 |
| `04_upgrade_cost_markov_chain.ipynb` | Markov chain cost model, Monte Carlo, tables and figures | 4, 5 |
| `05_contestation_survival_cox.ipynb` | Kaplan-Meier, Cox model, effect by round | 3 |
| `06_roll_or_level_calculator.ipynb` | Roll-or-level calculator | Appendix B |

Before committing, clear outputs (they can contain player ids and local paths):

    python scripts/clean_notebooks.py notebooks --check
    python scripts/clean_notebooks.py notebooks
