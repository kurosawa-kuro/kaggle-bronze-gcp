# 複数コンペ切替コスト削減アーキテクチャ実装

## Goal

ブロンズ取得まで複数 Kaggle コンペを切り替えて挑戦できるように、共通 runner に漏れているコンペ固有仕様を減らし、次コンペ投入時の変更箇所を `configs/<comp>/` と必要最小限の adapter に寄せる。

この task は [../idea/2026-07-06_multi-competition-architecture-review.md](../idea/2026-07-06_multi-competition-architecture-review.md) を実装単位へ落としたもの。

## Context

レビューで確認した主要リスクは以下。

- Vertex / local / stage-data の config 正本が分裂すると、新コンペで誤データ・誤 target・誤 metric のまま訓練する。
- 提出生成が `ID_COL + TARGET` 決め打ちだと、`sample_submission.csv` と列名・列順・形式が異なるコンペで即失敗する。
- FE / loader / submission / cache の責務境界が曖昧だと、次コンペのたびに共通 `src/` を直接編集することになる。
- metric 方向の重複実装は 2026-07-07 に解消済み。今後の metric 追加は registry に寄せる。

## Scope

### 実装対象

- P0-D: `sample_submission.csv` 正本化と `submission_contract.json` 永続化
- P1: feature registry の導入準備、`features:` config で FE を選べる構造への移行
- P1: BigQuery 比較 JOIN が `(competition, run_id)` で混線しないことの検証・不足修正
- P1: interim cache の stale 検知、または `make init` 時の安全な cache 退避・削除
- P2: `src/competitions/` escape hatch の導入判断と、必要な場合の最小 adapter 仕様化

### 完了済みとして扱うもの

- P0-A: config 単一正本化の止血
- P0-B: CV strategy registry と分割ロジック一本化
- P0-C: metric registry と最適化方向の一元化
- P0 系列の ROGII 参戦準備、マルチモデル + blend、Vertex full 完走

### 対象外

- 5責務すべてを持つ巨大 CompetitionPlugin
- YAML 変数展開
- cache config_hash 化
- ExperimentConfig の一括全面書換え
- Endpoint 常駐、Monitoring、Feature Store、KFP 細分化

## Skeleton

想定する最終構造は以下。

```text
configs/<comp>/
  baseline.yaml
  fe_*.yaml
src/
  pipelines/
    ingest.py
    featurize.py
    score.py
  features/
    __init__.py
  competitions/
    <comp>.py   # generic で足りない場合のみ
outputs/runs/<comp>/<run_id>/
  submission.csv
  submission_contract.json
```

## Plan

1. `score.py` / `train.py` / `blend.py` / `package_kernel.py` の提出生成経路を洗い出し、`sample_submission.csv` を読める共通 adapter 境界を決める。
2. `sample_submission.csv` がある場合は列名・列順・行数を正本にし、ない場合だけ従来の `id_col + submission_target` にフォールバックする。
3. run artifact に `submission_contract.json` を出力する。最低限、sample path、sample sha256、列名、行数、target columns、fallback 有無を記録する。
4. ROGII directory adapter と generic CSV の両方で submission 生成テストを追加する。
5. feature registry の最小設計を作り、`features: ["base"]` を config に足しても既存挙動が変わらない状態を作る。
6. BigQuery compare の JOIN と submission ledger のキーを確認し、同一 run_id が別 competition に存在しても混ざらないテストを追加する。
7. interim cache の stale 条件を定義し、schema mismatch 時に明示エラーか再生成へ倒す。
8. 実装が安定したら、この task を `done/` に移し、確定仕様を `docs/02_architecture.md` または runbook へ昇格する。

## Acceptance Criteria

- 新コンペで共通 `src/` を編集せず、最低限 `configs/<comp>/baseline.yaml` から smoke 実行に入れる。
- `sample_submission.csv` があるコンペでは、生成 `submission.csv` の列名・列順・行数が sample と一致する。
- 各 run に `submission_contract.json` が残り、提出形式の根拠を後から確認できる。
- ROGII 形式と generic CSV 形式の提出生成テストが通る。
- `compare` は `(competition, run_id)` で比較・コスト・提出履歴を結合し、コンペ跨ぎの同名 run_id で混線しない。
- stale interim cache を検知でき、別コンペの cache を黙って再利用しない。
- `PYTHONPATH=src .venv/bin/python -m unittest discover tests` が通る。

## Verification

実装時に最低限実行する。

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover tests
PYTHONPATH=src .venv/bin/python -m py_compile src/pipelines/score.py src/runner/experiment/train.py src/runner/ops/blend.py src/runner/ops/package_kernel.py
```

必要に応じて追加する。

```bash
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=multi_comp_submission_smoke
make compare LIMIT=5
```

## Notes

- この task の正本は実装チェックリスト。設計背景と根拠は idea 文書に残す。
- 完了済みの P0-A/B/C を再実装しない。必要な場合だけ regression test を追加する。
- `src/competitions/` は escape hatch として扱い、generic CSV + sample submission で表現できるコンペには使わない。
