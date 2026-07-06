# タスクコントロール

`docs/tasks/README.md` から参照される、毎日の作業開始時に最初に見る実行ハブ。**状態・順序・判断だけ**をここに置き、タスク詳細は各ノート、仕様は `docs/01〜08`、判断理由は `docs/adr/` に置く（重複させない）。

出典レビュー: [銅メダル戦略](../idea/2026-07-06_bronze-strategy-review.md) / [マルチコンペ切替再評価](../idea/2026-07-06_multi-competition-architecture-review.md)

## 現フェーズ: ROGII 参戦準備

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
| 1 | [P0-0 ROGII ルール確認](2026-07-06-p0-0-rogii-rules-check.md) | ✅ 2026-07-06 | なし | 0.5日 |
| 2 | [P0-A config 単一正本化](2026-07-06-p0-a-config-single-source.md) | ✅ 2026-07-06 | なし（P0-0 と並行可） | 1日 |
| 3 | [P0-1 CV strategy config 駆動化](2026-07-06-p0-1-cv-strategy-config.md) | ✅ 2026-07-06 | P0-A（group_col は P0-0） | 1〜2日 |
| 4 | [P0-2 package-kernel](2026-07-06-p0-2-package-kernel.md) | ✅ 2026-07-06 | **P0-0 完了必須**（持込方式が決まる） | 1〜2日 |
| 随時 | [P0-3 提出台帳](2026-07-06-p0-3-submissions-ledger.md) | 未着手 | なし。**初回提出前までに** | 0.5日 |
| 5 | [P0-4 マルチモデル + blend](2026-07-06-p0-4-multimodel-blend.md) | 未着手 | P0-A + P0-1 | 2〜3日 |

### ノート未作成の P0 候補（P0-0 の結果で作成判断）

| 候補 | 発動条件 |
|---|---|
| P0-C: metric registry + 方向一元化（tune/hp_tune/compare の3重複解消） | ROGII の指標が rmse/auc/logloss 以外なら**即 P0**。該当しなくても P1 上位 |
| P0-D: sample_submission 正本化 + submission_contract.json | ROGII は `id,tvt` の単純列だが、hidden test 置換型の Notebook 提出なので P0-E とセットで `sample_submission.csv` 正本化を実装する |
| P0-E: ROGII directory adapter | ROGII 初回提出前。`train/*.csv` / `test/*.csv` から `well_id` と sample row を組み立て、package kernel の標準CSV前提へ接続する |

## P1 キュー（ROGII 参戦後〜2週目）

- adversarial validation の標準成果物化（初週に1回、train/test ずれ診断）
- FE registry（`features:` リスト化。sweep の弾倉。ROGII 2週目の主戦場）
- `make init` の `configs/<comp>/baseline.yaml` 自動生成
- ROGII 形式の `make init` 対応（単一CSV前提から、directory dataset / loader scaffold 生成へ拡張）
- BQ JOIN を `(competition, run_id)` に修正（compare.py / submissions）
- interim cache の init 時自動削除 + schema hash 照合
- 失敗 run の台帳記録（status 列）
- Day-0 チェックリストのスキル化（ROGII Day 0 を実際にやりながら固める）

## P2（ROGII final 8/5 以降）

- BQ external table での SQL EDA（データサイズを見て判断）
- `src/competitions/` escape hatch（ROGII の loader が特殊と判明した時のみ前倒し）
- cfg 明示渡しへの段階移行（LABEL_CLASSES 排除・config.py global 退役）
- ports.py の実態合わせ or 削除 / `run.py`・notebooks の legacy 退役
- Cloud Build / 英語 README・アーキ図・ケーススタディ記事

## やらないこと

[銅メダル戦略レビュー セクション8](../idea/2026-07-06_bronze-strategy-review.md) を正とする（Endpoint 常駐 / Monitoring / Feature Store / KFP 細分化 / Batch Prediction の提出常用 / 全 run の Registry 登録 / stacking / HPO 深掘り / plugin 全面化 / YAML 変数展開 / cache config_hash 化）。

## リファクタリング候補（従来運用の継続）

日々見つかる cleanup 候補はここに1行で追記し、実行可能になったら task file 化する。

| # | 対象 | 内容 | 優先度 |
|---|------|------|--------|
| 1 | `src/models/catboost_.py:1` | 嘘 docstring「lgbm.py と同じシグネチャ」の修正（P0-4 で解消予定） | P0-4 内 |
| 2 | `scripts/init_competition.py` | `conf/config.yaml` 表記 drift（正は `env/`） | P1 init 強化内 |
| 3 | `src/runner/experiment/train.py:_trained_mask` | `oof != 0` の未学習判定を fold index ベースに | 低 |
| 4 | `metrics.json` | fold 別スコア・std の永続化（stdout のみ） | P0-3 とセット |

## 運用ルール

- タスクに着手したら状態を「進行中」に、完了したら「✅ + 完了日」にしてノートを `done/` へ移す。
- 判断が変わったら（繰上げ・却下・分割）この表を直し、理由が重ければ ADR へ昇格する。
- 週1回（月曜）、マイルストーンとの差分を見て P0/P1 の入れ替えを判断する。
- ドキュメント構成のルールは [../../00_index.md](../../00_index.md) を参照。
