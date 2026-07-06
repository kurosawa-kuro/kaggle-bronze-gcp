# Observed Change Signals

evidence_id: ev.change_signal.summary

This is git history evidence for files that changed often. It is not a defect claim.

| path | commit_count | churn | distinct_authors | last_changed |
|---|---:|---:|---:|---|
| `docs/02_architecture.md` | 15 | 770 | 1 | `2026-06-30T22:04:30+09:00` |
| `Makefile` | 14 | 312 | 1 | `2026-06-30T22:04:30+09:00` |
| `docs/01_requirements.md` | 13 | 337 | 1 | `2026-06-30T21:48:51+09:00` |
| `docs/04_workflows.md` | 12 | 507 | 1 | `2026-06-30T22:04:30+09:00` |
| `CLAUDE.md` | 12 | 206 | 1 | `2026-06-30T21:24:15+09:00` |
| `docs/05_data_model.md` | 10 | 511 | 1 | `2026-06-30T22:04:30+09:00` |
| `docs/08_release_runbook.md` | 6 | 136 | 1 | `2026-06-30T22:04:30+09:00` |
| `src/config.py` | 6 | 65 | 1 | `2026-06-30T22:04:30+09:00` |
| `docs/tasks/active/vertex-ready-runner.md` | 5 | 292 | 1 | `2026-06-30T22:04:30+09:00` |
| `docs/03_domain_model.md` | 5 | 189 | 1 | `2026-06-30T22:04:30+09:00` |
| `.gitignore` | 5 | 111 | 1 | `2026-06-30T22:04:30+09:00` |
| `docs/adr/0002-full-vertex-non-dl.md` | 5 | 74 | 1 | `2026-06-30T21:24:15+09:00` |
| `conf/project.yaml` | 5 | 68 | 1 | `2026-06-30T22:04:30+09:00` |
| `requirements.txt` | 5 | 16 | 1 | `2026-06-30T21:11:11+09:00` |
| `src/models/lgbm.py` | 4 | 127 | 1 | `2026-06-30T14:09:44+09:00` |
| `env/config.yaml` | 4 | 78 | 1 | `2026-06-30T22:04:30+09:00` |
| `docs/00_index.md` | 4 | 53 | 1 | `2026-06-30T20:37:38+09:00` |
| `run.py` | 4 | 43 | 1 | `2026-06-17T22:02:11+09:00` |
| `infra/Dockerfile` | 4 | 30 | 1 | `2026-06-30T22:04:30+09:00` |
| `catboost_info/catboost_training.json` | 3 | 9006 | 1 | `2026-06-17T22:02:11+09:00` |

## Notes

- churn = added + deleted lines from `git log --numstat`.
- binary file churn is counted as 0 when git reports `-`.
