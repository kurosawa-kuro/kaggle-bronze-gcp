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
   - 指標が evaluate.py 未対応 → **metric プラガブル化タスクを P0 に繰り上げて新規作成**（レビュー P1-2 の繰り上げ条件）
   - 事前学習モデルの Dataset 持込が不可 → P0-2 は「notebook 内で前処理再 fit + 学習」方式へ設計変更

## Acceptance Criteria

- [ ] 上記 Scope の 5 項目すべてが `docs/competitions/rogii-wellbore-geology-prediction.md` に根拠 URL 付きで記入されている
- [ ] P0-1（group_col）と P0-2（持込方式）への引き渡し判断が明文化されている
- [ ] 指標サポートの要否判断が記録され、未対応なら繰り上げタスクが作成されている
- 検証コマンド: `make init COMP=rogii-wellbore-geology-prediction` が完走し、`data/rogii-wellbore-geology-prediction/raw/` に train/test が正規化配置される

## 破綻条件

- ルールページの読み間違い（特に external data と pretrained models は別条項のことが多い）→ 原文引用をドキュメントに貼る
- 「たぶん code comp」の推測のまま P0-2 に着手する → このタスク完了を P0-2 の着手条件にする
