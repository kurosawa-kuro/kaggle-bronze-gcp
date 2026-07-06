# P0-4: CatBoost / XGBoost の runner 統合と OOF blend ops

## Goal

`model.name: catboost | xgboost` を config runner（train.py）に通し、`make blend RUN_IDS="a b c"` で複数 run の oof.parquet から blend した submission を作れるようにする。単発 LGBM から「モデル多様性 × blend」へ移行し、銅圏への押し込み手段を得る。

## Context

- 出典: [2026-07-06 銅メダル戦略レビュー](../idea/2026-07-06_bronze-strategy-review.md) P0-3。
- 現状 `train.py:176-177` が `model.name != lgbm` を明示 reject。`src/models/catboost_.py` / `xgboost_.py` は train_cv 実装済みだが正規経路（成果物契約・Vertex 投入・BQ 記録）に未接続。oof.parquet と `fold_manifest.json` の `valid_index_sha256` は全 run に既にあり、blend の安全機構として流用できる。
- 前提タスク: [P0-A](2026-07-06-p0-a-config-single-source.md) と [P0-1](2026-07-06-p0-1-cv-strategy-config.md)（全モデルが同じ splits を通ることが blend 整合の前提）。P0-2/P0-3 とは独立。
- コスト再見積もり（2026-07-06 再調査反映）: catboost_.py:1 の docstring「lgbm.py と同じシグネチャ」は**嘘**。実際は `(X, y, params, notes)` のみで n_folds / seed / max_folds / log_run_id を受けず、独自 `_splits` と独自 `_log` を持つ。シグネチャ統一を含むため実装コストは 2〜3日と見る。

## Scope

- In: train.py のモデルディスパッチ、catboost/xgboost の成果物契約準拠（oof/test_pred/model/manifest）、`configs/catboost_baseline.yaml`、blend ops（単純平均 → **rank averaging** → 重みグリッド探索の順に実装）、blend 結果の BQ 記録（source=blend）
- Out: stacking / 多段メタモデル（複雑化に対しリターンが薄い。レビュー「やらないこと」参照）、blend 対応 kernel パッケージ（P0-2 の後続として別タスク化）

## Plan

1. 着手時に `write-spec` で SPEC.md 化（変更: `src/runner/experiment/train.py`, `src/models/catboost_.py`, `src/models/xgboost_.py`, 新規 `src/runner/ops/blend.py`, `configs/`, Makefile）
2. train.py の `_train_lgbm` を `_train_model` に一般化し、model.name で train_cv をディスパッチ。seed 平均・成果物書き出し・hp_metric 報告は共通経路のまま
3. catboost/xgboost の train_cv シグネチャを lgbm と揃え（n_folds/seed/max_folds/early_stopping/log_run_id）、P0-1 の `_splits` を共用する
4. `blend.py`: 各 run の `fold_manifest.json` を読み **`valid_index_sha256` の全一致を必須アサート**（不一致は即エラー、上書きフラグは作らない）→ oof 上で (a) 単純平均 (b) rank average (c) 重みグリッドの CV を計算 → ベスト方式で test_pred を合成 → `outputs/runs/<comp>/<blend_run_id>/` に通常の成果物契約で保存 → BQ experiments に source=blend で記録
5. `make blend RUN_IDS="..." RUN_ID=<blend_id>` を Makefile に追加

## Acceptance Criteria

- [x] `make smoke CONFIG=configs/catboost_baseline.yaml` が通り、oof.parquet / test_pred.parquet / fold_manifest.json が LGBM run と同じ契約で出る
- [x] `make train-local CONFIG=configs/catboost_baseline.yaml RUN_ID=cat001` が通る
- [ ] `make train-vertex CONFIG=configs/catboost_baseline.yaml RUN_ID=cat_check` が Vertex でも完走する（イメージに catboost/xgboost を追加）
- [x] `make smoke CONFIG=configs/xgboost_baseline.yaml` が通り、multiclass probability を正規化した oof/test_pred/submission が出る
- [x] `make blend` が LGBM run + CatBoost run から blended submission を生成し、blend の OOF CV が単体ベストと同等以上であることを metrics.json で確認できる
- [x] fold_manifest 不一致の run を混ぜると明示エラーで止まる
- 検証コマンド: `make smoke CONFIG=configs/catboost_baseline.yaml` → `make train-local CONFIG=configs/catboost_baseline.yaml RUN_ID=cat001` → `make blend RUN_IDS="full_gcp_lgbm_001 cat001" RUN_ID=blend001` → `make compare`

## 2026-07-07 実装ログ

- `src/runner/experiment/train.py` を `model.name: lgbm | catboost | xgboost` の dispatcher に変更。seed bagging、OOF、test_pred、submission、model manifest は共通経路で保存する。
- `src/models/catboost_.py` / `src/models/xgboost_.py` の `train_cv` を LGBM と同じ runner signature に統一し、P0-1 の `pipelines.splits.make_splits` を共用化した。
- `src/runner/ops/blend.py` と `make blend` を追加。`fold_manifest.json` の `valid_index_sha256` 全一致を必須にし、mean / rank_average / 2-run weight grid から OOF CV 最良候補を選ぶ。
- `configs/catboost_baseline.yaml` / `configs/xgboost_baseline.yaml` を追加。
- 検証済み: `py_compile`、`PYTHONPATH=src .venv/bin/python -m unittest tests.test_blend tests.test_splits`、`make smoke CONFIG=configs/catboost_baseline.yaml RUN_ID=p04_cat_smoke`、`make smoke CONFIG=configs/xgboost_baseline.yaml RUN_ID=p04_xgb_smoke`、`make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=p04_lgbm_smoke`、`make blend CONFIG=configs/lgbm_baseline.yaml RUN_IDS="p04_lgbm_smoke p04_cat_smoke" RUN_ID=p04_blend_smoke`。
- smoke blend 結果: `p04_blend_smoke` は `weight_grid` の `[1.0, 0.0]` を選択し、OOF logloss `0.3276377551043895`。CatBoost smoke 単体 `0.4114301546818184`、LGBM smoke 単体 `0.3276377551043895` と同等以上を確認。
- full local 結果: `cat001` は 3 seeds × 5 folds の 15 boosters を保存し、OOF logloss `0.09465636124708839`。`oof.parquet` / `test_pred.parquet` / `fold_manifest.json` / `submission.csv` / `model/manifest.json` を確認済み。
- full blend 結果: `blend001` は `full_gcp_lgbm_001 + cat001` から生成成功。OOF logloss `0.08668087872662794`、best weight `[1.0, 0.0]`。
- Vertex full 結果: `make build-push` と `make stage-data CONFIG=configs/catboost_baseline.yaml` は成功。`make train-vertex CONFIG=configs/catboost_baseline.yaml RUN_ID=cat_check SYNC=--sync` は Vertex job `projects/941178142366/locations/us-central1/customJobs/8950973537221345280` を作成し、CatBoost fold 4/5 までは Cloud Logging で確認したが、`2026-07-06T17:02:56Z` 以降ログが止まり `JOB_STATE_RUNNING` のまま進捗停止したため、コスト抑止のため cancel。最終状態は `JOB_STATE_CANCELLED`。Vertex 完走は未達。
- 追加修正: `train.py` の trained mask を `oof != 0` から fold split 由来の validation index union に変更。`metrics.json` に seed 内 `fold_scores` と `fold_score_std`、全 fold の `fold_score_mean/std` を永続化した。
- 追加修正: `vertex_run.py` に guarded sync を追加。`--max-log-silence-minutes` と `--cancel-on-silence` で、worker log が止まった RUNNING job を自動キャンセルできる。`make train-vertex` はデフォルトで `--max-log-silence-minutes 10 --cancel-on-silence` を渡す。
- 追加検証: `make train-vertex CONFIG=configs/catboost_baseline.yaml RUN_ID=guard_dryrun SYNC=--sync DRY=--dry-run` が job を作成せず plan 表示で終了することを確認。誤って作成された dry-run 確認用 job `projects/941178142366/locations/us-central1/customJobs/3244068384412794880` は即 cancel 済み、最終状態 `JOB_STATE_CANCELLED`。
- 追加検証: `make smoke CONFIG=configs/catboost_baseline.yaml RUN_ID=p04_cat_guard_smoke` が成功し、`metrics.json` に fold scores が保存されることを確認。`PYTHONPATH=src .venv/bin/python -m unittest discover tests` は 9 tests OK。

## 破綻条件

- run 間で CV 分割が不一致のまま blend → OOF スコアが虚偽になる。valid_index_sha256 アサートで構造的に防止（このチェックを外す変更は禁止）
- catboost/xgboost の predict 出力形状（multiclass の proba 形状）が lgbm と不一致 → 成果物契約テストを1本置いて形状を固定
- 学習イメージへの catboost/xgboost 追加でイメージが肥大・ビルド失敗 → `make build-push` 後に Vertex smoke（KFP cache busting に注意。`project_gcp_verification` の既知事項）
- blend の重み探索を OOF に過剰適合させる → グリッドは粗く（0.1 刻み）、seed 平均済み oof のみを入力にする
