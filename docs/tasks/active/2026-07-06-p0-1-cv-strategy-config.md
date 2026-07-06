# P0-1: CV strategy の config 駆動化（GroupKFold 対応）

## Goal

`cv.strategy`（`kfold` / `stratified` / `group`）と `cv.group_col` を config で指定できるようにし、GroupKFold では fold 間の group overlap 検査を fold_manifest に永続化する。ROGII の well 単位 split を config 1枚で表現できる状態にする。

## Context

- 出典: [2026-07-06 銅メダル戦略レビュー](../idea/2026-07-06_bronze-strategy-review.md) P0-1（ランキング1位）。
- 現状は `src/models/lgbm.py:_splits()` が objective ベースで shuffle KFold / StratifiedKFold を固定選択する。ROGII（well 単位の空間データ）でこのままだと、リークした CV スコアを信じて private LB で崩れる。
- 前提タスク: [P0-A](2026-07-06-p0-a-config-single-source.md)（config 正本の止血。同じ train.py / models を触るため先行必須）。[P0-0](2026-07-06-p0-0-rogii-rules-check.md) で group_col 候補を確定してから ROGII 用 config を書く（実装自体は P0-0 完了前に着手可）。
- 実装方針の追記（2026-07-06 再調査反映）: `_splits` は lgbm.py 内の拡張ではなく、**新設 `src/pipelines/splits.py` に一本化**する。catboost_.py:65-68 に同一ロジックの重複実装があり、lgbm 側だけ直すと P0-4 で再手術になるため。

## Scope

- In: `_splits()` の strategy 分岐、`train.py:_write_fold_manifest` / `_write_leakage_audit` の group 検査、configs スキーマ拡張、ROGII 用 config 下書き
- Out: TimeSeriesSplit（`time` は将来枠として設計だけ考慮し実装しない）、CatBoost/XGBoost 側の対応（P0-4 で同じ `_splits` を使う前提の設計にはする）
- **後方互換**: `cv.strategy` 未指定なら現行挙動（regression→KFold / それ以外→StratifiedKFold）を厳密に維持する

## Plan

1. 着手時に `write-spec` で SPEC.md 化（変更ファイル: `src/models/lgbm.py`, `src/runner/experiment/train.py`, `src/config.py`, `configs/*.yaml`, `docs/02_architecture.md`）
2. `_splits(X, y, groups, *, strategy, n_folds, seed)` へ拡張。`group` は `GroupKFold`（shuffle 不可のため seed 平均との関係を docstring に明記）
3. `group` 時: featurize で drop される前の raw df から group 列を取り出して splitter に渡す配線を train.py に追加
4. fold_manifest に fold 間 group overlap 数（期待値 0）と fold ごとの group 数を記録。overlap > 0 なら学習を fail させる
5. leakage_audit に train/test の group 重複率を追加（well が test と重複するかは CV 設計の根拠になる）
6. ROGII 用 `configs/rogii_lgbm_baseline.yaml` を下書き（group_col は P0-0 の結果で確定）

## Acceptance Criteria

- [x] 既存 config（strategy 未指定）で `make smoke CONFIG=configs/lgbm_baseline.yaml` の fold_manifest が変更前と同一（`valid_index_sha256` 一致）
- [x] `cv.strategy: group` の config で smoke が通り、fold_manifest に `group_overlap: 0` が記録される
- [x] group overlap を人工的に起こすと検出できる（ユニットテスト1本）
- 検証コマンド: `make smoke CONFIG=configs/lgbm_baseline.yaml` / `make train-local CONFIG=<group指定config> RUN_ID=cv_group_check` / `.venv/bin/python -m pytest tests/ -k fold`

## 破綻条件

- group_col の指定ミス（存在しない列・null 混じり）→ 列存在と null 率を train.py 冒頭で検証して即エラー
- GroupKFold は shuffle/seed が効かないため、seed 平均が「モデル seed のみの平均」になる。これを仕様として metrics.json に明記しないと seed_scores の解釈を誤る
- 既定挙動が変わる regression → Acceptance 1 個目のハッシュ一致で検出する

## Verification

```bash
python3 -m py_compile src/pipelines/splits.py src/models/lgbm.py src/runner/experiment/train.py src/utils/logger.py
PYTHONPATH=src .venv/bin/python -m unittest tests.test_splits

make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=p01_default_smoke
# => success, cv_score=0.3276377551043895
# => fold_manifest first valid_index_sha256 matches p0a_smoke_check:
#    a0c61f781c12b7c4bb6397c3c8fd96dffaceb89ef04014f845cf5798f5440746

make smoke CONFIG=/tmp/p01_group_lgbm.yaml RUN_ID=p01_group_smoke
# => success, cv_score=0.327447210882202
# => fold_manifest strategy=group, group_col=id, group_overlap=0
```
