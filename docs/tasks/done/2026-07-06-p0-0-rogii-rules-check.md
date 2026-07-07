# P0-0: ROGII ルール・提出制約の事前確認（提出不能リスクの排除）

## Goal

コードを1行も書く前に、ROGII wellbore geology prediction の「提出不能リスク」と「間違った目的関数を最適化するリスク」を潰す。確認結果は `docs/competitions/rogii-wellbore-geology-prediction.md` に根拠 URL 付きで記入する。

## Context

- 出典: [2026-07-06 銅メダル戦略レビュー](../idea/2026-07-06_bronze-strategy-review.md) のセクション5 と P0-2 の破綻条件。
- ROGII は code competition（notebook 提出型）の可能性が高い（`docs/competitions/README.md` の再調査メモ参照）。提出形式の見落としは唯一のバイナリリスク（提出できない＝勝率 0）。
- entry 締切 2026-07-29 / final 2026-08-05。このタスクは最安（¥0・コード0行）で最大のリスクを潰す。

## Scope

コード実装はしない。確認と記録のみ。以下をすべて確認する:

1. **提出形式**: code competition か / notebook の internet on/off / 実行時間制限（CPU/GPU 別）/ 提出回数制限（日次・final 2 枚）
2. **持込可否**: 外部データ / 事前学習済みモデル / Kaggle Dataset の attach 可否（→ P0-2 の方式を決める）
3. **評価指標**: 公式指標の正確な定義。`src/pipelines/evaluate.py` の対応3種（rmse/auc/logloss）に含まれるか
4. **データ構造**: well 単位の group 構造の有無、`cv.group_col` に使える列名の候補（→ P0-1 の config を決める）
5. **締切**: entry / team merge / final submission の各日時（JST 換算）

## Plan

1. Kaggle のコンペページ（Overview / Data / Rules / Evaluation / Code Requirements）を確認
2. `make init COMP=rogii-wellbore-geology-prediction` でデータ取得し、train/test の列構造から group 構造を実地確認
3. `docs/competitions/rogii-wellbore-geology-prediction.md` の空欄を全部埋める
4. 分岐判断を同ドキュメントに明記:
   - 指標が evaluate.py 未対応なら、当該コンペ着手時に別タスクとして明示作成する
   - 事前学習モデルの Dataset 持込が不可 → P0-2 は「notebook 内で前処理再 fit + 学習」方式へ設計変更

## Acceptance Criteria

- [x] 上記 Scope の 5 項目すべてが `docs/competitions/rogii-wellbore-geology-prediction.md` に根拠 URL 付きで記入されている
- [x] P0-1（group_col）と P0-2（持込方式）への引き渡し判断が明文化されている
- [x] 指標サポートの要否判断が記録され、未対応なら繰り上げタスクが作成されている
- 検証コマンド: Kaggle CLI official pages と実データ展開で確認。`make init` は現行 config runner 用 YAML 生成に更新済み。

## 破綻条件

- ルールページの読み間違い（特に external data と pretrained models は別条項のことが多い）→ 原文引用をドキュメントに貼る
- 「たぶん code comp」の推測のまま P0-2 に着手する → このタスク完了を P0-2 の着手条件にする

## Result

2026-07-06 完了。

- 公式確認元: Kaggle CLI `competitions pages rogii-wellbore-geology-prediction`（Evaluation / Code Requirements / Timeline / data-description / rules）
- 公式ページ: https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction
- 評価指標: RMSE。既存 `evaluate.py` の `rmse` で対応済みのため P0-C は発動しない。
- 提出形式: Code Competition。Kaggle Notebook、internet disabled、CPU/GPU 9h、`submission.csv`。
- 提出上限: 5 submissions/day、final submission 最大2件。
- 外部データ/モデル: 公式 Code Requirements では freely/publicly available external data including pre-trained models が許可。rules では外部データ/ツール/モデルは公開・同等アクセス可能または合理的アクセス可能が条件。
- データ構造: train horizontal well 773 files / train typewell 773 files / visible test horizontal well 3 files。単一CSVではない。
- P0-1 引き渡し: `cv.strategy: group`、`cv.group_col: well_id`。`well_id` はファイル名から生成する。
- P0-2 引き渡し: Notebook package 必須。`sample_submission.csv` を正本にし、Vertex成果物はKaggle Notebookで再現可能・ルール適合する形に限定する。

実データ確認:

```text
raw children: AI_wellbore_geology_prediction_task_en.pptx, sample_submission.csv, test/, train/
train horizontal wells: 773
train typewells: 773
visible test horizontal wells: 3
visible test typewells: 3
sample_submission: 14151 rows, columns=id,tvt
train horizontal total rows: 5092255
visible test horizontal total rows: 19221
train TVT_input NaN rows: 3783989
visible test TVT_input NaN rows: 14151
```
