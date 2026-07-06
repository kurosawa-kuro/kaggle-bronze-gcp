# AGENTS.md

AI コーディングエージェント共通の作業ガイド。

## プロジェクト概要

- **目的**: Kaggle 表形式コンペでブロンズメダルを安定取得する
- **主要技術**: Python 3.12 / LightGBM / CatBoost / XGBoost / scikit-learn / GCP Vertex AI / GCS / BigQuery / Artifact Registry
- **実行環境**: WSL Ubuntu / uv 仮想環境 / GCP
- **現行方針**: 非 DL/GPU の GCP/Vertex マネージド機能は活用する。ADR 0002 を優先する

## セットアップ / 主要コマンド

```bash
make setup
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=smoke_check
make train-local CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001

make gcp-bootstrap
make stage-data
make build-push
make train-vertex CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001
make sweep CONFIGS="configs/lgbm_baseline.yaml configs/lgbm_deep.yaml" TAG=exp01
make hp-tune CONFIG=configs/lgbm_baseline.yaml RUN_ID=hpt01 MAX_TRIALS=20 PARALLEL=4
make collect CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001

make logs
make cost-record CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001
make cost
make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001 MSG="exp001"
```

`make run` は旧手動編集型の確認経路。再現可能な実験は `make smoke` / `make train-local` / `make train-vertex` を使う。

## ディレクトリ規約

| パス | 役割 |
|---|---|
| `configs/` | config runner 用 YAML。Vertex には base64 で渡すため config 変更だけなら image rebuild 不要 |
| `env/project.yaml` | GCP project / region / bucket / Artifact Registry / BigQuery / cost 設定 |
| `src/runner/experiment/` | train / Vertex submit / sweep / Optuna / HPT |
| `src/runner/model/` | Vertex Model Registry / Pipelines / Batch Prediction / Endpoint deploy |
| `src/runner/ops/` | GCS collect / Kaggle submit / cost logging |
| `src/models/` | モデル実装。config runner は現状 LightGBM が正規経路 |
| `src/features/` | FE アイデアごとに 1 ファイル |
| `src/utils/` | GCS / BigQuery / logger の最小 helper |
| `data/` | Kaggle 生データ（gitignore）。Vertex には `make stage-data` で GCS へ送る |
| `outputs/runs/` | local run_id 成果物（gitignore）。Vertex では同じ layout を GCS に保存 |
| `docs/` | 正本ドキュメント。判断は `docs/adr/`、タスク履歴は `docs/tasks/` |

## コーディング規約

- GCP/Vertex 実装を否定しない。現行方針は ADR 0002 の「非 DL/GPU の Vertex/GCP 機能を活用する」。
- 新しい GCP 機能を足す場合は、Makefile の 1 コマンド UX と `docs/04_workflows.md` を同時に更新する。
- tabular メタデータの正本は BigQuery `kaggle_ops`。SQLite 前提の新規実装は追加しない。
- blob / model / submission / oof は GCS と `outputs/runs/`。BigQuery に blob を入れない。
- Kaggle token は Vertex に持ち込まない。提出は local の Kaggle CLI 経由。
- 新 FE を追加するときは `src/features/` に新ファイルを作り、既存処理への副作用を小さくする。
- Port/Adapter・DI container・本番 Web アプリ水準の抽象は増やさない。
- LLM / RAG / Deep Learning / GPU 前提の提案はしない。LightGBM 主軸で解く。

## ドキュメント

設計・仕様・運用は `docs/` 配下を参照。更新規約と権威順位は `docs/00_index.md` に従う。
