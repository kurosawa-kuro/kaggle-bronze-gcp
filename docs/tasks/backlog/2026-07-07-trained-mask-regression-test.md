# _trained_mask_from_splits の回帰テスト追加

## Goal

fold index ベースの未学習判定 `_trained_mask_from_splits`（`src/runner/experiment/train.py`）に回帰テストを追加し、`max_folds` による部分 fold 学習時の mask が oof 値でなく split 由来で正しく立つことを保証する。

## Context

- リファクタ候補 #3（[2026-07-07-refactoring-candidates.md](../done/2026-07-07-refactoring-candidates.md)）で `oof != 0` 判定を fold index ベースに置き換えたが、テストなしで出荷された。旧 `_trained_mask` は 2026-07-07 の cleanup で削除済み。
- `tests/` は現状 pipelines / ops 層のみで、`train.py` 経路のテストがゼロ。
- 旧実装の欠陥: 正当な予測値 0（例: 回帰で oof=0.0）を「未学習」と誤判定する。この欠陥が再発しないことをテストで固定する。

## Scope

- 対象: `_trained_mask_from_splits` 単体（`make_splits` との結合を含む）。
- スコープ外: `run_training` 全体の E2E テスト、Vertex 経路、モデル学習の実行。

## Plan

- [ ] `tests/test_trained_mask.py` を作成する。
- [ ] ケース1: `max_folds=1`, `n_folds=5` で、fold 0 の valid index のみ True になること。
- [ ] ケース2: `max_folds=None`（全 fold）で全行 True になること。
- [ ] ケース3: oof に正当な 0.0 が含まれる状況でも mask が split 由来で立つこと（旧 `oof != 0` の欠陥の再発防止）。
- [ ] ケース4: `cv_strategy=group`（GroupKFold + groups 指定）でも同様に成立すること。
- [ ] `PYTHONPATH=src .venv/bin/python -m unittest discover tests` が全件 OK。

## Acceptance Criteria

- `_trained_mask_from_splits` を対象にしたテストが 3 ケース以上追加され、既存テストと合わせて全件 OK。
- 「予測値 0.0 を未学習と誤判定しない」ことを明示的に検証するケースが含まれる。
