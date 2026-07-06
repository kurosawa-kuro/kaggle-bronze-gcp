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

ROGII 実戦（entry 締切 2026-07-29）に向けた P0 系列。出典は [idea/2026-07-06_bronze-strategy-review.md](idea/2026-07-06_bronze-strategy-review.md)。実装順: P0-0 → P0-1 → P0-2 →（P0-3 は並行可）→ P0-4。

| ファイル | 用途 |
|---|---|
| [active/2026-07-06-p0-0-rogii-rules-check.md](active/2026-07-06-p0-0-rogii-rules-check.md) | ROGII ルール・提出形式・指標・group 構造の事前確認（コード0行、最優先） |
| [active/2026-07-06-p0-1-cv-strategy-config.md](active/2026-07-06-p0-1-cv-strategy-config.md) | CV strategy の config 駆動化（GroupKFold + fold overlap 検査） |
| [active/2026-07-06-p0-2-package-kernel.md](active/2026-07-06-p0-2-package-kernel.md) | code comp 用 package-kernel 経路（前処理状態の永続化を含む。P0-0 完了が着手条件） |
| [active/2026-07-06-p0-3-submissions-ledger.md](active/2026-07-06-p0-3-submissions-ledger.md) | BQ `submissions` 提出台帳 + `make lb-sync`（他タスクと並行可） |
| [active/2026-07-06-p0-4-multimodel-blend.md](active/2026-07-06-p0-4-multimodel-blend.md) | CatBoost/XGBoost 統合 + OOF blend ops（P0-1 が前提） |
| [active/refactoring-candidates.md](active/refactoring-candidates.md) | 残りのクリーンアップ候補 |

完了済み: [done/vertex-ready-runner.md](done/vertex-ready-runner.md) / [done/hpo-leverage-phase1.md](done/hpo-leverage-phase1.md) / [done/cost-tracking-bigquery.md](done/cost-tracking-bigquery.md)

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

次に着手できる作業は
[active/refactoring-candidates.md](active/refactoring-candidates.md) で管理する。
