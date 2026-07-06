# kaggle-bronze-gcp

Kaggle 表形式コンペでブロンズメダル圏を安定して狙うための、LightGBM 主軸・GCP/Vertex AI 活用型の実験基盤。

ローカルは EDA / smoke / 小実験、GCP は full run / seed 平均 / sweep / HPO / モデル登録 / バッチ推論に使う。実験成果物は local と GCS で同じ run_id レイアウトを保ち、実験・コストの tabular メタデータは BigQuery `kaggle_ops` に集約する。

## GCP フル検証済み

2026-07-06 に `run_id=full_gcp_lgbm_001` で、GCP/Vertex 上の本番級経路を end-to-end 完走済み。

| 段階 | 検証結果 |
|---|---|
| Terraform | `infra/terraform` plan = `No changes` |
| 訓練・評価 | Vertex Custom Job `projects/941178142366/locations/us-central1/customJobs/5462847664892674048` が `JOB_STATE_SUCCEEDED` |
| 実験台帳 | BigQuery `kaggle_ops.experiments` に seed run と aggregate run を記録 |
| CV | aggregate `cv_score=0.08668087872662794` |
| 成果物 | GCS から `outputs/runs/playground-series-s6e6/full_gcp_lgbm_001/` へ回収済み |
| モデル登録 | Vertex Model Registry `projects/941178142366/locations/us-central1/models/3101590910316576768@1` |
| 推論 | Vertex Batch Prediction `projects/941178142366/locations/us-central1/batchPredictionJobs/8231488312376819712` が `JOB_STATE_SUCCEEDED` |
| 推論件数 | `247435 / 247435` 件成功 |

## 技術スタック

| レイヤー | 技術 |
|---|---|
| 言語 | Python 3.12 |
| 主モデル | LightGBM（config runner の正規経路） |
| 既存モデル実装 | CatBoost / XGBoost / ensemble |
| 前処理・評価 | pandas / scikit-learn |
| HPO | Optuna / Vertex AI Hyperparameter Tuning |
| 実験実行 | local / Vertex AI Custom Job / Vertex Pipelines |
| 成果物 | `outputs/runs/<comp>/<run_id>/` / GCS |
| メタデータ | BigQuery `kaggle_ops.experiments`, `kaggle_ops.cost_estimates` |
| コンテナ | Docker / Artifact Registry |
| 推論 | Vertex Model Registry / Batch Prediction / Endpoint deploy code |
| 仮想環境 | uv |

## セットアップ

```bash
make setup
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=smoke_check
```

GCP 経路を使う前に `env/project.yaml` の project / region / bucket / Artifact Registry repo / BigQuery dataset を確認し、Terraform plan を見る。

```bash
make terraform-init
make terraform-plan
make stage-data
make build-push
```

## 基本ワークフロー

```bash
# ローカル smoke
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=smoke_lgbm

# ローカル full run
make train-local CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001_lgbm

# Vertex Custom Job
make train-vertex CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001_lgbm

# 複数 config を Vertex に並列投入
make sweep CONFIGS="configs/lgbm_baseline.yaml configs/lgbm_deep.yaml" TAG=exp01

# HPO
make tune CONFIG=configs/lgbm_baseline.yaml RUN_ID=tune01 N_TRIALS=30
make hp-tune CONFIG=configs/lgbm_baseline.yaml RUN_ID=hpt01 MAX_TRIALS=20 PARALLEL=4

# 成果物回収・ログ・コスト
make collect CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001_lgbm
make logs
make cost-record CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001_lgbm
make cost
make compare
```

提出:

```bash
make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001_lgbm MSG="exp001 lgbm baseline"
```

## GCP 対応状況

| 領域 | 状態 |
|---|---|
| GCS data staging / artifact collect | 実装済み |
| Artifact Registry 学習 image | 実装済み |
| Vertex Custom Job | 実装済み |
| Vertex Hyperparameter Tuning | 実装済み |
| Vertex Model Registry | 実装済み |
| Vertex Pipelines | 実装済み（compile / submit 経路） |
| Vertex Batch Prediction | 実装済み。`full_gcp_lgbm_001` で全件推論成功済み |
| Vertex Endpoint | deploy / teardown コード実装済み。常駐コストのため手動・任意 |
| BigQuery 実験ログ / コストログ | 実装済み（google-cloud-bigquery Python client） |
| Terraform | 導入済み。GCS / Artifact Registry / BigQuery / Vertex SA / IAM / Budget を管理 |
| Cloud Build / GitHub Actions | 未導入。ローカル Makefile から投入 |

## ディレクトリ構成

```text
configs/                  # config runner 用 YAML
env/
  config.yaml             # 旧 run 経路 / default config
  project.yaml            # GCP project / region / bucket / image / BQ
  secret.yaml             # gitignore。Kaggle token / Discord webhook 等
infra/
  Dockerfile              # Vertex 学習コンテナ
  Dockerfile.serving      # Vertex Batch / Endpoint 推論コンテナ
  terraform/              # GCP 基盤 IaC
src/
  runner/
    experiment/           # train / vertex_run / sweep / tune / hp_tune
    model/                # register / pipeline / batch_predict / deploy
    ops/                  # collect / submit / costs / compare
  pipelines/              # ingest / featurize / evaluate / score
  models/                 # lgbm / catboost / xgboost / ensemble
  serving/                # Vertex 推論コンテナ本体
  utils/                  # GCS / BigQuery / logger
data/                     # gitignore。Kaggle raw data
outputs/runs/             # gitignore。run_id 成果物
docs/                     # 正本ドキュメント
```

詳細は [docs/00_index.md](docs/00_index.md) を参照。
