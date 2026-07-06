# Investigated Findings

generated_by: dcm investigate
source: non_llm_evidence_investigation
judgment_status: llm_enriched

## observed_signals

- Evidence Pack exists and has the required scan, symbol, config, risk, and scan-limitation files. evidence_ref: file=evidence/00_scan_manifest.md
- Symbol evidence exists for code navigation and candidate responsibility boundaries. evidence_ref: file=evidence/03_symbols.md
- Configuration and environment evidence exists for secret and runtime-risk review. evidence_ref: file=evidence/08_config_env.md
- Static signal evidence exists and must be investigated before draft. evidence_ref: file=evidence/30_static_signal_hits.md
- Scan limitation evidence exists and can inform descriptive current implications when judgment-relevant. evidence_ref: file=evidence/99_scan_limitations.md

## available_evidence_files

- `00_evidence_freshness.md`
- `00_scan_manifest.md`
- `01_file_tree.md`
- `02_files.json`
- `03_symbols.md`
- `04_symbols.json`
- `05_tests.md`
- `07_entrypoints.md`
- `08_config_env.md`
- `09_diff_evidence.md`
- `10_observed_change_signals.json`
- `10_observed_change_signals.md`
- `11_dependency_inventory.json`
- `11_dependency_inventory.md`
- `12_code_metrics.json`
- `12_code_metrics.md`
- `13_public_api_surface.json`
- `13_public_api_surface.md`
- `14_code_excerpts.json`
- `14_code_excerpts.md`
- `15_decision_memory.json`
- `15_decision_memory.md`
- `30_static_signal_hits.md`
- `98_redaction_report.md`
- `99_scan_limitations.md`

## llm_enrichment

## item_meaning_candidates

- `src/runner/experiment/train.py` appears to be the primary training orchestrator, comprising argument parsing, config resolution, model training (LGBM at least), artifact writing, and stdout tee-ing. Reference: symbols in `evidence/03_symbols.md` for `src/runner/experiment/train.py`.
- `src/serving/predictor.py` implements a custom HTTP `Handler` (`do_GET`, `do_POST`) that loads a `Predictor` class for inference, and references AI Platform (AIP) environment variables (`AIP_HEALTH_ROUTE`, `AIP_HTTP_PORT`, `AIP_PREDICT_ROUTE`, `AIP_STORAGE_URI`). Reference: `evidence/08_config_env.md` (AIP_* env vars), `evidence/03_symbols.md` (`Predictor`, `Handler`).
- `src/runner/ops/costs.py` records Vertex AI usage costs and sends Discord notifications via `DISCORD_WEBHOOK_URL`. Reference: `evidence/08_config_env.md` for `DISCORD_WEBHOOK_URL`; symbols in `evidence/03_symbols.md` for functions `record_vertex`, `report`, `notify`.
- `src/pipelines/featurize.py` contains `make_features` and `src/pipelines/ingest.py` contains `load_data`, suggesting a data pipeline that loads from CSV or California housing dataset and encodes features. Reference: `evidence/03_symbols.md` for those symbols.
- `src/utils/artifact_store.py` provides GCS upload/download and `latest_run_id` utility, indicating reliance on Google Cloud Storage for artifacts. Reference: symbols in `evidence/03_symbols.md`.
- `src/utils/bq.py` exposes BigQuery query and insert operations, suggesting logging or storing results to BigQuery. Reference: symbols in `evidence/03_symbols.md`.
- The presence of `src/models/ensemble.py` with an `average` function and separate model modules (`lgbm`, `xgboost_`, `catboost_`) suggests ensemble averaging as a prediction strategy. Reference: `evidence/03_symbols.md`.
- `infra/Dockerfile` uses `python:3.12-slim` as base image and sets `PYTHONPATH`. Reference: `evidence/08_config_env.md` for `PYTHONPATH`; `evidence/03_symbols.md` for container-base-image.

## role_notes

- `src/pipelines/` modules (`ingest`, `featurize`, `score`, `evaluate`) form a classic ML data pipeline: ingest → featurize → score (predict) → evaluate (CV score). Reference: symbols in `evidence/03_symbols.md`.
- `src/models/` modules each expose a `train_cv` function and internal helper `_splits` and `_log`, indicating a consistent cross‑validation interface across LightGBM, XGBoost, CatBoost, and ensemble. Reference: `evidence/03_symbols.md` for each model file.
- `src/runner/experiment/` hosts experiment‑level orchestration: `train.py`, `tune.py` (hyperparameter tuning with Optuna per `notebooks/optuna_lgbm.py`), `hp_tune.py`, `sweep.py`, and `vertex_run.py` for submitting to Vertex AI. Reference: symbols in `evidence/03_symbols.md`.
- `src/runner/model/` manages model deployment lifecycle: `register.py` (register from run), `deploy.py` (deploy/teardown), `batch_predict.py`, and `pipeline.py` (build Vertex AI pipeline). Reference: symbols in `evidence/03_symbols.md`.
- `src/utils/` provides infrastructure utilities: artifact store (GCS), BigQuery, logger, and config. Reference: symbols in `evidence/03_symbols.md`.
- The entrypoints (`scripts/init_competition.py`, `src/runner/run.py`, etc.) indicate distinct invocation modes: data initialization, experiment runs, serving, and ops (costs, collect, submit). Reference: `evidence/07_entrypoints.md` (not provided in full but entrypoint_count=16 suggests many). The symbols in `evidence/03_symbols.md` also show `main` functions in multiple scripts.
- `notebooks/optuna_lgbm.py` contains an Optuna `objective` function, likely used for hyperparameter search outside the main experiment orchestration. Reference: `evidence/03_symbols.md`.

## current_implications

- Serving is designed to run on Google Cloud AI Platform (AIP) due to the presence of `AIP_` environment variables and the `Handler` class with health and predict routes. Reference: `evidence/08_config_env.md` (AIP_* entries) and `evidence/03_symbols.md` (predictor.py symbols).
- Cost tracking via Vertex AI and Discord notifications is actively implemented, implying operational monitoring. Reference: `evidence/30_static_signal_hits.md` (high_risk_ops matched 11 hits) and `evidence/08_config_env.md` (`DISCORD_WEBHOOK_URL`).
- Several documentation files (`docs/01_requirements.md`, `docs/02_architecture.md`, `docs/04_workflows.md`) and `CLAUDE.md` have observed change signals, indicating active documentation evolution. Reference: `evidence/30_static_signal_hits.md` (`change_signal:*` entries).
- The project uses multiple model implementations (LGBM, XGBoost, CatBoost) with a common CV interface, suggesting the user runs benchmarks or ensemble experiments. Reference: `evidence/03_symbols.md` (model files).
- The `_write_dummy_artifacts` function in `train.py` (symbol L277) suggests the training pipeline can produce placeholder artifacts, possibly for debugging or CI. Reference: `evidence/03_symbols.md`.
- No tests are detected (`test_count: 0` in `evidence/00_scan_manifest.md`), which implies either tests are absent, excluded, or not captured by the scan (e.g., in unsupported extensions). Reference: `evidence/00_scan_manifest.md`.
- The scan detected no TODO comments (`todos` no_hit in `evidence/30_static_signal_hits.md`), though that does not prove absence (per scan limitations).
- `src/ports.py` defines abstract interfaces (`ModelTrainer`, `FeatureTransformer`), but their concrete implementations are not statically resolvable to specific classes, suggesting dependency injection or dynamic dispatch. Reference: `evidence/03_symbols.md`.

## uncertainty_notes

- Requiredness and default values for all environment variables are unknown; the scan only recorded names/references. Reference: `evidence/08_config_env.md` (value redacted, requiredness unknown).
- The symbol extraction is heuristic‑based; dynamic code (e.g., decorator‑registered endpoints, class‑factory functions) may be missed. Reference: `evidence/99_scan_limitations.md` (parser limitations).
- The absence of test files (`test_count: 0`) may be due to test files having unsupported extensions (e.g., `.csv`, `.parquet`) or being in directories excluded by `.gitignore`; not confirmed absence. Reference: `evidence/99_scan_limitations.md` and `evidence/00_scan_manifest.md`.
- The “no-hit” for `todos` does not guarantee no TODOs exist; grep depends on query vocabulary. Reference: `evidence/30_static_signal_hits.md` (guardrail) and `evidence/99_scan_limitations.md`.
- The relationship between the Optuna notebook (`notebooks/optuna_lgbm.py`) and the experiment tuning scripts (`src/runner/experiment/tune.py`) is unclear from static symbols alone — they may share logic or be separate workflows.
- `src/ports.py` interfaces (`ModelTrainer`, `FeatureTransformer`) have no concrete static bindings; the runtime wiring is not visible in the evidence.
- The `secret` values (e.g., `DISCORD_WEBHOOK_URL`) are redacted; actual secrets may be present in the repository but are excluded from the scan output. Reference: `evidence/08_config_env.md` and `evidence/30_static_signal_hits.md` (env_secret matched 37, but content redacted).
- The scan manifest notes unsupported extensions (`.csv`, `.parquet`, `.serving`, `.tfevents`, `.tsv`) which could contain additional configuration or model artifacts not analyzed. Reference: `evidence/00_scan_manifest.md`.
- The `src/runner/ops/collect.py` and `src/runner/ops/submit.py` functions have limited documented purpose from symbols; their exact behavior is not fully derivable.

## judgment_value_added

- Raw inventory has been classified into draft inputs: observed signals, roles, and current implications.
- LLM enrichment, when present, adds meaning for each evidence item without changing observed evidence.
- This file does not approve an implementation choice or prescribe future work. It prevents raw scan output from being treated as a completed Decision Catalog.

## draft_inputs

- Draft must create `catalog_items` where each item pairs fact and meaning.
- Draft must not include advice, recommendations, next actions, validation plans, rollback plans, or change boundaries.
- Draft must cite evidence_ids for fact items and must not invent facts outside the Evidence Pack.

## required_llm_enrichment

- Assign role/current implication to evidence items.
- Keep risk language descriptive and current-state only.
- Put judgment-relevant uncertainty in descriptive current implications instead of a separate field.

## next_step

- Run `dcm draft <TARGET>` or `dcm llm draft <TARGET>` only after this investigated findings file exists.
