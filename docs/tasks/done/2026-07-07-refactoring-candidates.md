# タスクコントロール

`docs/tasks/README.md` から参照される、毎日の作業開始時に最初に見る実行ハブ。**状態・順序・判断だけ**をここに置き、タスク詳細は各ノート、仕様は `docs/01〜08`、判断理由は `docs/adr/` に置く（重複させない）。

出典レビュー: [銅メダル戦略](../idea/2026-07-06_bronze-strategy-review.md) / [マルチコンペ切替再評価](2026-07-06_multi-competition-architecture-review.md)

## 現フェーズ: ROGII 参戦準備

現ゴール（P0 系列 / P0-4 マルチモデル + blend / Vertex full 完走）は **2026-07-07 に残作業なしで完了**。active task はゼロ。完了証跡は `docs/tasks/done/` に集約済み。

| マイルストーン | 期日 | 状態 |
|---|---|---|
| P0-0 完了（参戦 go/no-go 判断） | 2026-07-07 | ✅ 2026-07-06 |
| ROGII 初回 notebook 提出 | 2026-07-13（理想） | 未 |
| ROGII entry 締切 | **2026-07-29（固定）** | — |
| ROGII final submission | **2026-08-05（固定）** | — |

## ステータスボード（P0 系列）

実行順の原理: **情報 → 止血 → 正しさ → 提出可否 → スコア押し込み**

| 順 | タスク | 状態 | 前提 | 目安 |
|---|---|---|---|---|
| 1 | [P0-0 ROGII ルール確認](../done/2026-07-06-p0-0-rogii-rules-check.md) | ✅ 2026-07-06 | なし | 0.5日 |
| 2 | [P0-A config 単一正本化](../done/2026-07-06-p0-a-config-single-source.md) | ✅ 2026-07-06 | なし（P0-0 と並行可） | 1日 |
| 3 | [P0-1 CV strategy config 駆動化](../done/2026-07-06-p0-1-cv-strategy-config.md) | ✅ 2026-07-06 | P0-A（group_col は P0-0） | 1〜2日 |
| 4 | [P0-2 package-kernel](../done/2026-07-06-p0-2-package-kernel.md) | ✅ 2026-07-06 | **P0-0 完了必須**（持込方式が決まる） | 1〜2日 |
| 随時 | [P0-3 提出台帳](../done/2026-07-06-p0-3-submissions-ledger.md) | ✅ 2026-07-06 | なし。**初回提出前までに** | 0.5日 |
| 5 | [P0-E ROGII directory adapter](../done/2026-07-06-p0-e-rogii-directory-adapter.md) | ✅ 2026-07-06 | P0-0 + P0-1 + P0-2 | 0.5〜1日 |
| 6 | [P0-4 マルチモデル + blend](../done/2026-07-06-p0-4-multimodel-blend.md) | ✅ 2026-07-07 | P0-A + P0-1 | 2〜3日 |

### ノート未作成の P0 候補

なし。P0 系列は完了済み。

## Active Task

なし。

## やらないこと

[銅メダル戦略レビュー セクション8](../idea/2026-07-06_bronze-strategy-review.md) を正とする（Endpoint 常駐 / Monitoring / Feature Store / KFP 細分化 / Batch Prediction の提出常用 / 全 run の Registry 登録 / stacking / HPO 深掘り / plugin 全面化 / YAML 変数展開 / cache config_hash 化）。

## リファクタリング候補（従来運用の継続）

日々見つかる cleanup 候補はここに1行で追記し、実行可能になったら task file 化する。

| # | 対象 | 内容 | 優先度 |
|---|------|------|--------|
| 1 | `src/models/catboost_.py:1` | 嘘 docstring「lgbm.py と同じシグネチャ」の修正 | ✅ 2026-07-07 |
| 2 | `scripts/init_competition.py` | 旧 config 表記 drift を現行 `configs/<comp>_baseline.yaml` 生成へ修正 | ✅ 2026-07-07 |
| 3 | `src/runner/experiment/train.py:_trained_mask` | `oof != 0` の未学習判定を fold index ベースに | ✅ 2026-07-07 |
| 4 | `metrics.json` | fold 別スコア・std の永続化（stdout のみ） | ✅ 2026-07-07 |
| 5 | `src/runner/experiment/vertex_run.py` | Vertex full が RUNNING のまま進捗停止した時の guarded sync / auto-cancel | ✅ 2026-07-07 |

## 運用ルール

- タスクに着手したら状態を更新し、完了したら「✅ + 完了日」にしてノートを `done/` へ移す。
- 判断が変わったら（繰上げ・却下・分割）この表を直し、理由が重ければ ADR へ昇格する。
- 新しい作業を始める場合は、別タスクとして明示作成してから着手する。
- ドキュメント構成のルールは [../../00_index.md](../../00_index.md) を参照。
