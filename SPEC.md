# SPEC: GCP / Vertex 実験基盤の現行仕様

このファイルは、GCP 対応済みの現行仕様を新しい作業セッションへ渡すための短い正本メモ。過去の Phase1 実装スペックは完了済みで、詳細な運用は `docs/01_requirements.md`〜`docs/08_release_runbook.md` と ADR 0002 を優先する。

## Goal

Kaggle ブロンズ取得に必要な表形式実験を、local と GCP/Vertex の両方で同じ run_id 契約で回す。

- local: EDA / smoke / 小実験 / Kaggle 提出
- Vertex: full run / seed 平均 / 複数 config sweep / HPO / pipeline / model registry / batch prediction
- BigQuery: 実験ログとコストログ
- GCS: raw data staging と run_id artifact storage
- Artifact Registry: 学習・推論コンテナ

## Current GCP Surface

| 機能 | コマンド / 実装 | 状態 |
|---|---|---|
| GCP bootstrap | `make gcp-bootstrap` | API / AR repo / GCS bucket の最小作成 |
| 学習 image | `make build-push`, `infra/Dockerfile` | Artifact Registry push |
| data staging | `make stage-data` | `data/<comp>/raw` を GCS へ upload |
| Vertex Custom Job | `make train-vertex`, `runner.experiment.vertex_run` | 実装済み |
| sweep | `make sweep`, `runner.experiment.sweep` | 複数 Custom Job を非ブロッキング投入 |
| Optuna | `make tune`, `runner.experiment.tune` | local / 単一マシン探索 |
| Vertex HPT | `make hp-tune`, `runner.experiment.hp_tune` | Vizier managed HPO |
| artifact collect | `make collect`, `runner.ops.collect` | GCS → local |
| experiment logs | `make logs`, `utils.logger` | BigQuery `kaggle_ops.experiments` |
| cost logs | `make cost-record`, `make cost`, `runner.ops.costs` | BigQuery `kaggle_ops.cost_estimates` |
| Model Registry | `make register-model`, `make register-servable` | Vertex Model Registry |
| Pipelines | `make pipeline` | KFP train → register |
| serving image | `make build-push-serving`, `infra/Dockerfile.serving` | Batch / Endpoint 共用 |
| Batch Prediction | `make batch-predict` | serving image 付き model が前提 |
| Endpoint | `make endpoint-deploy`, `make endpoint-teardown` | コードあり。常駐コストのため手動・任意 |

## Non-goals

- GCP/Vertex の否定やローカル単機への後退
- SQLite を実験ログ正本に戻すこと
- Ray / Spark / MLflow サーバ / GKE / Cloud Composer など、ブロンズ目的に対して運用負荷が大きい基盤
- DL / GPU / LLM / RAG
- Terraform / Cloud Build / GitHub Actions の導入を現行仕様として書くこと。必要なら別タスク・別 ADR で追加する

## Invariants

- `runner.experiment.train` は local / Vertex 共通の学習契約。
- Vertex submitter は config YAML を base64 で渡す。config 変更だけなら image rebuild 不要。
- `data/` は Docker image に含めない。Vertex は GCS staging から読む。
- run_id 成果物は local と GCS で同じ layout。
- tabular メタデータは BigQuery、blob は GCS。
- Kaggle token は Vertex に持ち込まない。
- Endpoint は 24/7 課金されるため、使う場合だけ deploy し、必ず teardown する。

## Verification

```bash
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=smoke_check
PYTHONPATH=src .venv/bin/python -m runner.experiment.vertex_run \
  --config configs/lgbm_baseline.yaml --run-id dryrun_check --dry-run
make -n train-vertex CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp_check
make -n sweep CONFIGS="configs/lgbm_baseline.yaml configs/lgbm_deep.yaml" TAG=check
make -n hp-tune CONFIG=configs/lgbm_baseline.yaml RUN_ID=hpt_check MAX_TRIALS=4 PARALLEL=2
```

GCP 実投入はコストと認証を確認してから実行する。
