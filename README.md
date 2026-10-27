# K26 Turnout Estimator

Live Central Elections Committee turnout per ballot box, multiplied by each box's 2022 bloc split and scaled to the final TV polls (Kan 11, Channel 12, Channel 13 at weight 1; Channel 14 at weight 0.3), projected to a final vote and seat estimate. Hebrew and English (`#en` for English).

- Site: `docs/` (served by GitHub Pages from `main` / `docs`)
- Data refresh: `.github/workflows/refresh.yml` runs every 10 minutes, downloads the latest turnout snapshot, rebuilds `docs/data.json` with `scripts/prep.py`, and commits it if it changed.

## Data and license

Turnout and the 2022 ballot-box results come from [Kolot Nodedim](https://github.com/harelc/elections-vote-transfer) by Harel Cain, which pulls the CEC feeds and matches every 2026 ballot box to its 2022 twin. That work is licensed CC BY-NC-SA 4.0, so this site is too: credit the source, no commercial use, and share derivatives under the same license.

This is an estimate from turnout only. No votes have been counted.
