# Data (not included)

The analysis uses ranked NA Challenger matches collected through the Riot Games API
(1,000 matches played 15 September to 7 October 2026). The raw files contain
player identifiers, so they are **not** committed (see `.gitignore`) and are not
distributed here. Check Riot's developer policy before sharing any raw match data.

Expected files, if you rebuild them yourself:

- `boards.csv`: one row per player per match (match_id, board_id, placement, last_round, level, ...)
- `units.csv`: one row per unit on a board (match_id, board_id, unit, tier, rarity, items)
- `boards_clustered.csv`: written by notebook 02 (comp family per board)

The cost model and the web app do **not** need these files: the parameters they use
(copies per competitor `H`, background depletion `BG`) are stored in `tftcost/model.py`.
