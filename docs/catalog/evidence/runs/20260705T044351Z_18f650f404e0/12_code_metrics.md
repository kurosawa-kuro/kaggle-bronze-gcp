# Code Metrics

evidence_id: ev.code_metrics.summary

Deterministic size and symbol-count signals. These are risk-prioritization signals, not defect claims.

| path | language | loc | non_empty_loc | symbols | public_symbols | tests | max_line_length |
|---|---|---:|---:|---:|---:|---:|---:|
| `configs/lgbm_baseline.yaml` | `github-actions` | 33 | 29 | 0 | 0 | 0 | 96 |
| `configs/lgbm_deep.yaml` | `github-actions` | 28 | 24 | 0 | 0 | 0 | 32 |
| `doppler.yaml` | `github-actions` | 74 | 65 | 0 | 0 | 0 | 112 |
| `env/config.yaml` | `github-actions` | 20 | 16 | 0 | 0 | 0 | 73 |
| `env/project.yaml` | `github-actions` | 33 | 31 | 0 | 0 | 0 | 106 |
| `env/secret.example.yaml` | `github-actions` | 9 | 7 | 0 | 0 | 0 | 99 |
| `env/secret.yaml` | `github-actions` | 15 | 13 | 0 | 0 | 0 | 140 |
| `infra/Dockerfile` | `dockerfile` | 22 | 16 | 1 | 1 | 0 | 87 |
| `notebooks/exp001_lgbm_base.py` | `python` | 12 | 10 | 0 | 0 | 0 | 71 |
| `notebooks/exp002_catboost_base.py` | `python` | 12 | 10 | 0 | 0 | 0 | 75 |
| `notebooks/exp003_ensemble_lgbm_cat.py` | `python` | 24 | 19 | 0 | 0 | 0 | 91 |
| `notebooks/optuna_lgbm.py` | `python` | 90 | 76 | 1 | 1 | 0 | 109 |
| `scripts/init_competition.py` | `python` | 170 | 137 | 6 | 5 | 0 | 177 |
| `src/config.py` | `python` | 29 | 23 | 0 | 0 | 0 | 97 |
| `src/features/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/features/stellar.py` | `python` | 22 | 17 | 1 | 1 | 0 | 107 |
| `src/models/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/models/catboost_.py` | `python` | 76 | 59 | 3 | 1 | 0 | 98 |
| `src/models/ensemble.py` | `python` | 11 | 9 | 1 | 1 | 0 | 93 |
| `src/models/lgbm.py` | `python` | 97 | 81 | 3 | 1 | 0 | 109 |
| `src/models/xgboost_.py` | `python` | 82 | 66 | 3 | 1 | 0 | 98 |
| `src/pipelines/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/pipelines/evaluate.py` | `python` | 15 | 12 | 1 | 1 | 0 | 71 |
| `src/pipelines/featurize.py` | `python` | 40 | 32 | 1 | 1 | 0 | 110 |
| `src/pipelines/ingest.py` | `python` | 78 | 60 | 4 | 2 | 0 | 94 |
| `src/pipelines/score.py` | `python` | 47 | 36 | 2 | 2 | 0 | 102 |
| `src/ports.py` | `python` | 34 | 27 | 4 | 3 | 0 | 112 |
| `src/runner/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/runner/experiment/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/runner/experiment/hp_tune.py` | `python` | 122 | 107 | 1 | 1 | 0 | 133 |
| `src/runner/experiment/sweep.py` | `python` | 49 | 40 | 1 | 1 | 0 | 119 |
| `src/runner/experiment/train.py` | `python` | 389 | 329 | 22 | 4 | 0 | 131 |
| `src/runner/experiment/tune.py` | `python` | 121 | 96 | 6 | 3 | 0 | 115 |
| `src/runner/experiment/vertex_run.py` | `python` | 179 | 157 | 6 | 2 | 0 | 127 |
| `src/runner/model/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/runner/model/batch_predict.py` | `python` | 141 | 119 | 4 | 2 | 0 | 129 |
| `src/runner/model/deploy.py` | `python` | 152 | 128 | 6 | 3 | 0 | 127 |
| `src/runner/model/pipeline.py` | `python` | 179 | 149 | 8 | 4 | 0 | 128 |
| `src/runner/model/register.py` | `python` | 222 | 187 | 9 | 2 | 0 | 148 |
| `src/runner/ops/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/runner/ops/collect.py` | `python` | 49 | 37 | 3 | 1 | 0 | 116 |
| `src/runner/ops/costs.py` | `python` | 209 | 171 | 12 | 4 | 0 | 121 |
| `src/runner/ops/submit.py` | `python` | 49 | 41 | 2 | 1 | 0 | 101 |
| `src/runner/run.py` | `python` | 29 | 25 | 1 | 1 | 0 | 94 |
| `src/serving/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/serving/predictor.py` | `python` | 118 | 92 | 12 | 7 | 0 | 119 |
| `src/utils/__init__.py` | `python` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/utils/artifact_store.py` | `python` | 75 | 61 | 6 | 6 | 0 | 94 |
| `src/utils/bq.py` | `python` | 58 | 45 | 5 | 5 | 0 | 108 |
| `src/utils/logger.py` | `python` | 79 | 67 | 4 | 2 | 0 | 113 |

## Guardrail

- Large files and many public symbols increase review attention; they do not prove unsafe code.
