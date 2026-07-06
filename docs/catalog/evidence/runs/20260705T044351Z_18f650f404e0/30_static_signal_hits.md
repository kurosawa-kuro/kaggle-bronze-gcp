# Static Signal Hits

This is a machine-generated signal inventory, not a decision.
Every row points back to grep evidence.

| query_id | hit_state | hits | evidence_ref | follow_up |
|---|---|---:|---|---|
| `todos` | `no_hit` | 0 | `file=evidence/grep/01_todos.md query_id=todos` | treat as no-hit, not absence |
| `job_lifecycle` | `matched` | 62 | `file=evidence/grep/02_job_lifecycle.md query_id=job_lifecycle` | review matching lines before deciding |
| `env_secret` | `matched` | 37 | `file=evidence/grep/03_env_secret.md query_id=env_secret` | review matching lines before deciding |
| `high_risk_ops` | `matched` | 11 | `file=evidence/grep/04_high_risk_ops.md query_id=high_risk_ops` | review matching lines before deciding |
| `auth_permission` | `matched` | 14 | `file=evidence/grep/05_auth_permission.md query_id=auth_permission` | review matching lines before deciding |
| `infra_surface` | `matched` | 93 | `file=evidence/grep/06_infra_surface.md query_id=infra_surface` | review matching lines before deciding |
| `change_signal:docs/02_architecture.md` | `observed` | 15 | `file=evidence/10_observed_change_signals.md path=docs/02_architecture.md` | inspect change history before editing |
| `change_signal:Makefile` | `observed` | 14 | `file=evidence/10_observed_change_signals.md path=Makefile` | inspect change history before editing |
| `change_signal:docs/01_requirements.md` | `observed` | 13 | `file=evidence/10_observed_change_signals.md path=docs/01_requirements.md` | inspect change history before editing |
| `change_signal:docs/04_workflows.md` | `observed` | 12 | `file=evidence/10_observed_change_signals.md path=docs/04_workflows.md` | inspect change history before editing |
| `change_signal:CLAUDE.md` | `observed` | 12 | `file=evidence/10_observed_change_signals.md path=CLAUDE.md` | inspect change history before editing |

## Guardrail

- Static signal entries are observations only. Decision Catalog claims still need explicit `evidence_ref` values.
