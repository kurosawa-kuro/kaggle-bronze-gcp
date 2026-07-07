# タスク

このディレクトリは、毎日の作業計画・調査・実装チェックリスト・完了証跡の実行ハブ。プロダクトの挙動・アーキテクチャ・データモデル・運用 runbook の正本ではないが、「今日何をするか」「次に何をするか」「何を完了したか」はここを正とする。

着手前の機能スペックは root `SPEC.md`、確定した仕様は `docs/01〜08`、判断は `docs/adr/`、再利用する作業手順は `.claude/skills/` に置く。

## 日次運用

1. 作業開始時に `active/` を見る。
2. 今日やることを 1 つ選び、必要なら task file を作る。
3. 実装前に Scope / Plan / Acceptance Criteria を更新する。
4. 作業中の判断、検証コマンド、未解決事項を task file に残す。
5. 完了時に証跡を追記し、必要なら `done/` へ移す。
6. 着手前のスペックは root `SPEC.md`、確定した仕様は 01〜08 文書へ昇格する。
7. 判断理由として残すべき内容は `docs/adr/` へ昇格する。

`tasks/` は軽く保つが、軽すぎて運用履歴が消えるのは避ける。日々の作業で迷ったら、まず task に書いてから実装へ進む。

## 構成

| ディレクトリ | 用途 |
|---|---|
| `backlog/` | まだ着手準備ができていない / 予定が未定の候補 |
| `active/` | 進行中、または次に実行するもの |
| `done/` | 完了したタスクノート。必要なら判断を ADR に昇格する |

## タスクの粒度

- 1 task は、1 つの目的と 1 つの完了条件を持つ。
- 1 日で終わらない task は、今日やるチェック項目を `Plan` に切り出す。
- 大きすぎる task は `backlog/` に分割案を置き、実行単位だけ `active/` に出す。
- 仕様変更、設計判断、運用手順が固まったら、task に閉じ込めず docs 本体へ昇格する。

## 関連スキル

| スキル | 用途 |
|---|---|
| `.claude/skills/write-spec` | 公式 spec-driven で着手前に自己完結スペックを root `SPEC.md` に書く |
| `.claude/skills/create-task` | ユーザー依頼から軽量な日次タスクノートを作る |
| `.claude/skills/execute-task` | 挙動とテストを保ったままタスクを実行する |
| `.claude/skills/review-task` | 範囲・根拠・クローズ可否の観点でタスクをレビューする |
| `.claude/skills/project-review` | プロジェクト構成と責務境界をレビューする |
| `.claude/skills/refactor-plan` | 早すぎる共通化を避けてリファクタを計画する |
| `.claude/skills/hallucination-check` | 結論前に主張をファイルとコマンドで検証する |
| `.claude/skills/skeleton-first` | テスト・実装の前にビジネスロジックレスのスケルトンで構造を固定する |

## Active

active task は現在 0 件。P0 系列（ROGII 参戦準備、マルチモデル + blend、Vertex full 完走）、複数コンペ切替コスト削減、完了タスク監査は完了し、証跡は `done/` と docs 本体に反映済み。

| ファイル | 用途 |
|---|---|
| なし | 進行中タスクなし |

## Done Snapshot

直近で完了確認済みの主要 task。

| ファイル | 状態 |
|---|---|
| [done/2026-07-06-p0-0-rogii-rules-check.md](done/2026-07-06-p0-0-rogii-rules-check.md) | ROGII ルール・提出制約確認済み |
| [done/2026-07-06-p0-a-config-single-source.md](done/2026-07-06-p0-a-config-single-source.md) | runner config 単一正本化済み |
| [done/2026-07-06-p0-1-cv-strategy-config.md](done/2026-07-06-p0-1-cv-strategy-config.md) | CV strategy / GroupKFold 対応済み |
| [done/2026-07-06-p0-2-package-kernel.md](done/2026-07-06-p0-2-package-kernel.md) | package-kernel 最小経路済み |
| [done/2026-07-06-p0-3-submissions-ledger.md](done/2026-07-06-p0-3-submissions-ledger.md) | BigQuery 提出台帳済み |
| [done/2026-07-06-p0-e-rogii-directory-adapter.md](done/2026-07-06-p0-e-rogii-directory-adapter.md) | ROGII directory adapter 済み |
| [done/2026-07-06-p0-4-multimodel-blend.md](done/2026-07-06-p0-4-multimodel-blend.md) | CatBoost / XGBoost / blend / Vertex full 完走済み |
| [done/2026-07-06_multi-competition-architecture-review.md](done/2026-07-06_multi-competition-architecture-review.md) | 複数コンペ切替アーキテクチャ再評価、実装済み項目反映済み |
| [done/2026-07-07_multi-competition-switching-hardening.md](done/2026-07-07_multi-competition-switching-hardening.md) | sample submission 正本化、contract、FE registry、cache stale 検知済み |
| [done/2026-07-07-refactoring-candidates.md](done/2026-07-07-refactoring-candidates.md) | P0 系列完了時点の cleanup 証跡 |

## Latest Verification

2026-07-07 の完了タスク監査で、壊れた done リンク、古い active 参照、古い LGBM-only 記述、`configs/<comp>/baseline.yaml` 表記揺れを修正済み。

検証:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover tests
# 20 tests OK
```

完了済みの主要仕様は `docs/01_requirements.md`〜`docs/08_release_runbook.md` と `docs/adr/` に昇格済み。完了 task の証跡は `done/` に置く。

## ルール

ここにタスク詳細を重複させない。各タスクファイルは軽く保つ:

```markdown
# タスクタイトル

## Goal

## Context

## Scope

## Skeleton

## Plan

## Acceptance Criteria

## Verification

## Notes
```

次に着手できる作業・実行順・マイルストーンは、`active/` の task file で管理する。
