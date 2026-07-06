# Public API Surface

evidence_id: ev.public_api_surface.summary

Public/exported symbols observed by deterministic heuristics. Use this as blast-radius evidence before classifying a bounded change.

| path | line | language | kind | name | parent |
|---|---:|---|---|---|---|
| `infra/Dockerfile` | 1 | `dockerfile` | `container-base-image` | `python:3.12-slim` | `` |
| `notebooks/optuna_lgbm.py` | 38 | `python` | `function` | `objective` | `` |
| `scripts/init_competition.py` | 20 | `python` | `function` | `download` | `` |
| `scripts/init_competition.py` | 49 | `python` | `function` | `normalize` | `` |
| `scripts/init_competition.py` | 79 | `python` | `function` | `analyze` | `` |
| `scripts/init_competition.py` | 133 | `python` | `function` | `create_doc` | `` |
| `scripts/init_competition.py` | 147 | `python` | `function` | `main` | `` |
| `src/features/stellar.py` | 6 | `python` | `function` | `add_stellar_fe` | `` |
| `src/models/catboost_.py` | 19 | `python` | `function` | `train_cv` | `` |
| `src/models/ensemble.py` | 5 | `python` | `function` | `average` | `` |
| `src/models/lgbm.py` | 27 | `python` | `function` | `train_cv` | `` |
| `src/models/xgboost_.py` | 24 | `python` | `function` | `train_cv` | `` |
| `src/pipelines/evaluate.py` | 8 | `python` | `function` | `cv_score` | `` |
| `src/pipelines/featurize.py` | 14 | `python` | `function` | `make_features` | `` |
| `src/pipelines/ingest.py` | 11 | `python` | `function` | `load_data` | `` |
| `src/pipelines/ingest.py` | 57 | `python` | `function` | `encode` | `` |
| `src/pipelines/score.py` | 12 | `python` | `function` | `predict` | `` |
| `src/pipelines/score.py` | 17 | `python` | `function` | `make_submission` | `` |
| `src/ports.py` | 11 | `python` | `class` | `ModelTrainer` | `` |
| `src/ports.py` | 16 | `python` | `method` | `train_cv` | `ModelTrainer` |
| `src/ports.py` | 26 | `python` | `class` | `FeatureTransformer` | `` |
| `src/runner/experiment/hp_tune.py` | 20 | `python` | `function` | `main` | `` |
| `src/runner/experiment/sweep.py` | 15 | `python` | `function` | `main` | `` |
| `src/runner/experiment/train.py` | 83 | `python` | `function` | `main` | `` |
| `src/runner/experiment/train.py` | 104 | `python` | `function` | `run` | `` |
| `src/runner/experiment/train.py` | 364 | `python` | `method` | `write` | `_Tee` |
| `src/runner/experiment/train.py` | 370 | `python` | `method` | `flush` | `_Tee` |
| `src/runner/experiment/tune.py` | 40 | `python` | `function` | `run` | `` |
| `src/runner/experiment/tune.py` | 72 | `python` | `function` | `objective` | `` |
| `src/runner/experiment/tune.py` | 107 | `python` | `function` | `main` | `` |
| `src/runner/experiment/vertex_run.py` | 31 | `python` | `function` | `submit_from_config` | `` |
| `src/runner/experiment/vertex_run.py` | 136 | `python` | `function` | `main` | `` |
| `src/runner/model/batch_predict.py` | 20 | `python` | `function` | `submit_batch` | `` |
| `src/runner/model/batch_predict.py` | 109 | `python` | `function` | `main` | `` |
| `src/runner/model/deploy.py` | 20 | `python` | `function` | `deploy` | `` |
| `src/runner/model/deploy.py` | 69 | `python` | `function` | `teardown` | `` |
| `src/runner/model/deploy.py` | 126 | `python` | `function` | `main` | `` |
| `src/runner/model/pipeline.py` | 27 | `python` | `function` | `build_and_run` | `` |
| `src/runner/model/pipeline.py` | 70 | `python` | `function` | `train_op` | `` |
| `src/runner/model/pipeline.py` | 79 | `python` | `function` | `register_op` | `` |
| `src/runner/model/pipeline.py` | 151 | `python` | `function` | `main` | `` |
| `src/runner/model/register.py` | 24 | `python` | `function` | `register_from_run` | `` |
| `src/runner/model/register.py` | 180 | `python` | `function` | `main` | `` |
| `src/runner/ops/collect.py` | 21 | `python` | `function` | `main` | `` |
| `src/runner/ops/costs.py` | 61 | `python` | `function` | `record_vertex` | `` |
| `src/runner/ops/costs.py` | 151 | `python` | `function` | `report` | `` |
| `src/runner/ops/costs.py` | 163 | `python` | `function` | `notify` | `` |
| `src/runner/ops/costs.py` | 173 | `python` | `function` | `main` | `` |
| `src/runner/ops/submit.py` | 22 | `python` | `function` | `main` | `` |
| `src/runner/run.py` | 20 | `python` | `function` | `main` | `` |
| `src/serving/predictor.py` | 52 | `python` | `class` | `Predictor` | `` |
| `src/serving/predictor.py` | 63 | `python` | `method` | `predict` | `Predictor` |
| `src/serving/predictor.py` | 79 | `python` | `class` | `Handler` | `` |
| `src/serving/predictor.py` | 88 | `python` | `method` | `do_GET` | `Handler` |
| `src/serving/predictor.py` | 94 | `python` | `method` | `do_POST` | `Handler` |
| `src/serving/predictor.py` | 106 | `python` | `method` | `log_message` | `Handler` |
| `src/serving/predictor.py` | 110 | `python` | `function` | `main` | `` |
| `src/utils/artifact_store.py` | 9 | `python` | `class` | `GcsPrefix` | `` |
| `src/utils/artifact_store.py` | 14 | `python` | `method` | `parse` | `GcsPrefix` |
| `src/utils/artifact_store.py` | 23 | `python` | `method` | `uri` | `GcsPrefix` |
| `src/utils/artifact_store.py` | 29 | `python` | `function` | `upload_directory` | `` |
| `src/utils/artifact_store.py` | 45 | `python` | `function` | `download_directory` | `` |
| `src/utils/artifact_store.py` | 63 | `python` | `function` | `latest_run_id` | `` |
| `src/utils/bq.py` | 15 | `python` | `function` | `clean_env` | `` |
| `src/utils/bq.py` | 21 | `python` | `function` | `load_gcp` | `` |
| `src/utils/bq.py` | 31 | `python` | `function` | `query` | `` |
| `src/utils/bq.py` | 42 | `python` | `function` | `lit` | `` |
| `src/utils/bq.py` | 54 | `python` | `function` | `insert_row` | `` |
| `src/utils/logger.py` | 46 | `python` | `function` | `log_run` | `` |
| `src/utils/logger.py` | 69 | `python` | `function` | `show_runs` | `` |

## Guardrail

- Public-by-convention for Python means names not starting with `_`; confirm package exports before API promises.
