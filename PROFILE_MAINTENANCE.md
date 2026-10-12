# Profile maintenance

- `README.md` is published from the private career-profile repository (`data/brand/kit.json`, `build/brand/publish_github.sh`). Edit it there, then publish.
- `.github/workflows/stats.yml` runs every day at 02:30 UTC. It runs `.github/scripts/build_stats.py`, which reads the public contribution calendars of AC-e-AI and FutureAtoms, keeps the highest daily count ever seen in `stats/history.json`, and writes the dark and light cards in `stats/`. It commits only when something changed.
- Private work counts toward the cards only when the account shows private contributions (profile, Contribution settings, Private contributions).
