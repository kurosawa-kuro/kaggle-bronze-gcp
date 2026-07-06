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

- [ ] `make smoke CONFIG=configs/catboost_baseline.yaml` と `make train-local` が通り、oof.parquet / test_pred.parquet / fold_manifest.json が LGBM run と同じ契約で出る
- [ ] `make train-vertex CONFIG=configs/catboost_baseline.yaml RUN_ID=cat_check` が Vertex でも完走する（イメージに catboost/xgboost を追加）
- [ ] `make blend` が LGBM run + CatBoost run から blended submission を生成し、blend の OOF CV が単体ベストと同等以上であることを metrics.json で確認できる
- [ ] fold_manifest 不一致の run を混ぜると明示エラーで止まる
- 検証コマンド: `make smoke CONFIG=configs/catboost_baseline.yaml` → `make train-local CONFIG=configs/catboost_baseline.yaml RUN_ID=cat001` → `make blend RUN_IDS="full_gcp_lgbm_001 cat001" RUN_ID=blend001` → `make compare`

## 破綻条件

- run 間で CV 分割が不一致のまま blend → OOF スコアが虚偽になる。valid_index_sha256 アサートで構造的に防止（このチェックを外す変更は禁止）
- catboost/xgboost の predict 出力形状（multiclass の proba 形状）が lgbm と不一致 → 成果物契約テストを1本置いて形状を固定
- 学習イメージへの catboost/xgboost 追加でイメージが肥大・ビルド失敗 → `make build-push` 後に Vertex smoke（KFP cache busting に注意。`project_gcp_verification` の既知事項）
- blend の重み探索を OOF に過剰適合させる → グリッドは粗く（0.1 刻み）、seed 平均済み oof のみを入力にする
