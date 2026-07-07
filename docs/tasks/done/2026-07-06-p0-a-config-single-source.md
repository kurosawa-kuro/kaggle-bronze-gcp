# P0-A: config 単一正本化の止血（Vertex config 無視バグの修正）

## Goal

runner 経路（smoke / train-local / train-vertex / sweep / hp-tune）で、**渡した CONFIG が local / Vertex を問わず常に正本**になる状態を作る。「コンペ切替＝env/config.yaml 書き換え＋イメージ再ビルド」という現状の暗黙運用を撲滅する。

## Context

- 出典: [複数コンペ切替アーキテクチャ再評価](../idea/2026-07-06_multi-competition-architecture-review.md) セクション4 #1〜#4。
- 確認済みバグ: Vertex 実行では `train.py:140-145` の `--input-uri` staging が `KBC_CONFIG_PATH` 設定（`train.py:168`）より先に `from config import DATA_RAW` を実行するため、config module がイメージにベイクされた `env/config.yaml`（`infra/Dockerfile:14`）で確定・キャッシュされる。以後 ingest / featurize / evaluate / lgbm が読む TARGET / OBJECTIVE / METRIC は全部ベイク値になり、`--config-b64` の data セクションは無視される。
- `full_gcp_lgbm_001` が成功したのは env/config.yaml と渡した config が同一コンペだったから。ROGII の config を投げた瞬間に顕在化する。
- 併発: `Makefile` の `COMP_DATA` が env/config.yaml から comp を読むため、`make stage-data CONFIG=configs/new.yaml` は旧コンペの raw を GCS へ上げる。
- **後続の P0-1（CV config 駆動化）/ P0-4（マルチモデル）は同じファイル群を触るため、これを先にやらないと手戻りになる。**

## Scope

- In: runner 経路の config 正本統一（3点の最小修正）と docs の実行契約明記
- Out: `src/config.py` global 定数の全面オブジェクト化、legacy 経路（`run.py` / `notebooks/`）の修正、registry 系の追加拡張

## Plan

1. `train.py:run()` の先頭（`--input-uri` staging と一切の `from config import` より前）に `os.environ["KBC_CONFIG_PATH"] = str(config_path)` を設定（`_train_lgbm` 内の既存設定は残してよい）
2. `Makefile` の `COMP_DATA` を `$(CONFIG)` の `data.comp` から読むよう変更（`stage-data` が CONFIG に追従）
3. `utils/logger.py:log_run()` に `competition` / `metric` の明示引数（省略時は現行 global fallback）を追加し、train.py 経由の記録を config 値で確定させる
4. `docs/02_architecture.md` の Vertex 実行契約に「`--config-b64` が data セクション含め正本。env/config.yaml は legacy `make run` / notebooks 専用」と明記
5. 小規模だが影響が広いので、着手時に `write-spec` で SPEC.md 化してから実施

## Acceptance Criteria

- [x] **env/config.yaml を意図的に別コンペ設定のままにして**、`make smoke CONFIG=configs/lgbm_baseline.yaml` の metrics.json / BQ 記録の competition・metric が CONFIG 側の値になる
- [x] 同条件で `KBC_CONFIG_PATH` 未設定のプロセスから `python -m runner.experiment.train --config-b64 <...> --input-uri <ローカル代替>` 相当を実行し、staging 先ディレクトリと TARGET が CONFIG 側になる（Vertex バグの再現テストを潰した証明）
- [x] `make stage-data CONFIG=configs/lgbm_baseline.yaml` の upload 先が CONFIG の comp になる（dry 確認で可）
- [x] 既存の正常系が不変: `make smoke` / `make train-local` の成果物契約・fold_manifest ハッシュに差分がない
- 検証コマンド: 上記 + `make train-vertex CONFIG=... --dry-run`（plan JSON の input/output URI が CONFIG の comp を指す）

## 破綻条件

- config.py の import タイミングが他 entrypoint（tune.py / hp_tune.py は既に `os.environ` 設定→import の順で安全）と食い違う → 全 entrypoint で「KBC_CONFIG_PATH 設定が最初」の規約を grep で確認
- env/config.yaml との flat/nested スキーマ差 → `config.py:14-19` は両対応済みだが、念のため nested config を KBC_CONFIG_PATH に渡す単体テストを1本置く
- legacy `make run` / notebooks を巻き込んで肥大 → スコープ外を厳守（env/config.yaml はそのまま残す）

## Verification

```bash
python3 -m py_compile src/runner/experiment/train.py src/utils/logger.py
make -n stage-data CONFIG=configs/lgbm_baseline.yaml
# => gcloud storage cp --recursive data/playground-series-s6e6/raw gs://mlops-dev-a-kaggle-bronze-runs/data/playground-series-s6e6/

PYTHONPATH=src .venv/bin/python -m runner.experiment.vertex_run --config configs/lgbm_baseline.yaml --run-id p0a_dry --dry-run
# => input_uri/output_uri が configs/lgbm_baseline.yaml の data.comp を指す

make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=p0a_smoke_check
# => 成功、BQ kaggle_ops.experiments へ run_id=p0a_smoke_check / logloss / playground-series-s6e6 を記録
```
