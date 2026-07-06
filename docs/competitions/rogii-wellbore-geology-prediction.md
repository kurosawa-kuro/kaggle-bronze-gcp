# rogii-wellbore-geology-prediction

> Kaggle URL: https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction  
> 確認日: 2026-07-06
> 公式確認元: Kaggle Competition pages / Kaggle CLI `competitions pages rogii-wellbore-geology-prediction`

## 結論

| 項目 | 判断 |
|---|---|
| 参戦可否 | Go |
| 提出方式 | **Code Competition**。Kaggle Notebook から `submission.csv` を生成して提出 |
| Notebook 制約 | Internet disabled / CPU 9h 以下 / GPU 9h 以下 |
| 提出上限 | 5 submissions/day、final submission は最大2件 |
| 評価指標 | RMSE。既存 `src/pipelines/evaluate.py` の `rmse` で対応済み |
| データ構造 | well ごとのファイル分割。CSV単表ではない |
| CV 方針 | `cv.strategy: group`、`cv.group_col: well_id`。`well_id` はファイル名から生成する |
| P0-2 方針 | Notebook package 必須。GCP/Vertex の重い探索はローカル/Vertexで行い、提出時はKaggle Notebookで再現可能な推論パッケージにする |

## 公式ルール・提出制約

| 項目 | 内容 | 根拠 |
|---|---|---|
| 公式ページ | `https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction` | Kaggle competition page |
| Code Requirements | Submissions must be made through Notebooks | Kaggle CLI page `Code Requirements` |
| Notebook runtime | CPU Notebook <= 9 hours / GPU Notebook <= 9 hours | Kaggle CLI page `Code Requirements` |
| Internet | Internet access disabled | Kaggle CLI page `Code Requirements` |
| Submission file | `submission.csv` | Kaggle CLI page `Code Requirements` |
| External data / pretrained models | Freely and publicly available external data is allowed, including pre-trained models | Kaggle CLI page `Code Requirements` |
| External data general rule | External data/tools/models must be publicly/equally accessible or reasonably accessible at minimal cost | Kaggle CLI page `rules`, section 6 |
| Daily submissions | 5 submissions/day | Kaggle CLI page `rules`, Submission Limits |
| Final submissions | up to 2 final submissions | Kaggle CLI page `rules`, Submission Limits |
| Team size | max 5 | Kaggle CLI page `rules`, Competition Specific Rules |
| Private sharing | private sharing outside team is prohibited | Kaggle CLI page `rules`, Individuals and Teams |

P0-2 への持込判断:

- GCP/Vertex での HPO、重い学習、実験管理は活用してよい。
- ただし最終提出は Kaggle Notebook 上で `submission.csv` を作る必要がある。
- Vertex で作ったモデル成果物を Notebook に持ち込む場合、Kaggle Dataset attach 前提になる。外部データ/モデルは「公開・同等アクセス可能・合理的なコスト」が条件なので、非公開の独自外部モデルを前提にしない。
- Competition data から自分で学習した推論 artifact の扱いは P0-2 で最小Notebook提出を通して確認する。不可または不確実なら Notebook 内で前処理と学習を再実行する方式に倒す。

## 締切

公式 Timeline は UTC 11:59 PM 基準。JST 換算は +9h。

| 項目 | UTC | JST |
|---|---:|---:|
| Start Date | 2026-05-05 23:59 | 2026-05-06 08:59 |
| Working Note Award optional deadline | 2026-07-06 23:59 | 2026-07-07 08:59 |
| Entry Deadline | 2026-07-29 23:59 | 2026-07-30 08:59 |
| Team Merger Deadline | 2026-07-29 23:59 | 2026-07-30 08:59 |
| Final Submission Deadline | 2026-08-05 23:59 | 2026-08-06 08:59 |

## 評価指標・提出形式

| 項目 | 内容 |
|---|---|
| Official metric | RMSE |
| 目的変数 | `TVT` / submission column は lowercase `tvt` |
| Submission columns | `id,tvt` |
| `id` format | `{WELLNAME}_{row_index}` |
| sample rows | `sample_submission.csv`: 14,151 rows, 2 columns |

`evaluate.py` 判断:

- `metric: rmse` で既存対応済み。
- P0-C metric registry は ROGII 参戦の blocker ではない。
- ただし tune / hp_tune / compare の metric 重複は P1 上位候補として残す。

## データ概要

| 項目 | 内容 |
|---|---|
| raw 配置 | `data/rogii-wellbore-geology-prediction/raw/` |
| train horizontal wells | 773 files |
| train typewells | 773 files |
| visible test horizontal wells | 3 files |
| visible test typewells | 3 files |
| train horizontal total rows | 5,092,255 |
| visible test horizontal rows | 19,221 |
| sample_submission rows | 14,151 |
| horizontal train columns | `MD`, `X`, `Y`, `Z`, `ANCC`, `ASTNU`, `ASTNL`, `EGFDU`, `EGFDL`, `BUDA`, `TVT`, `GR`, `TVT_input` |
| horizontal test columns | `MD`, `X`, `Y`, `Z`, `GR`, `TVT_input` |
| typewell train columns | `TVT`, `GR`, `Geology` |
| typewell test columns | `TVT`, `GR` |
| train `TVT_input` null rows | 3,783,989 |
| visible test `TVT_input` null rows | 14,151 |
| group key | file stem before `__`, e.g. `000d7d20` |

公式 Data Description 要約:

- データは horizontal well trajectories と vertical reference logs (Typewells) で構成される。
- 各 well は一意な 8 文字 hash で識別される。
- train では horizontal well に `TVT` と `TVT_input` があり、`TVT_input` は evaluation zone が NaN。
- hidden test では visible `test/` が置き換わるため、Notebook はディレクトリ走査と `sample_submission.csv` 基準で行IDを作る。

## env/config.yaml / runner config 方針

ROGII は既存の単一 `train.csv` / `test.csv` 前提から外れるため、P0-E で competition-specific loader または notebook packaging 側の adapter を追加する。

```yaml
comp: rogii-wellbore-geology-prediction
competition:
  slug: rogii-wellbore-geology-prediction
data:
  comp: rogii-wellbore-geology-prediction
  raw_dir: data/rogii-wellbore-geology-prediction/raw
target: TVT
submission_target: tvt
id_col: id
objective: regression
metric: rmse
n_folds: 5
seed: 42
cv:
  strategy: group
  group_col: well_id
```

## リーク候補・CV 方針

| リスク | 方針 |
|---|---|
| 同一 well の近傍行が train/valid にまたがる | `GroupKFold` を使い、`well_id` 単位でfold分割する |
| `TVT_input` の NaN zone | evaluation zone の位置情報としては使えるが、targetそのものを漏らさない特徴量処理が必要 |
| formations (`ANCC` など) | train horizontal にはあるが test horizontal にはない。hidden testでも使えない前提で直接特徴量にしない |
| visible test が train由来サンプル | visible 3 well だけに合わせた分岐を禁止。`sample_submission.csv` とディレクトリ構造を正本にする |

P0-1 引き渡し:

- `cv.strategy: group`
- `cv.group_col: well_id`
- `well_id` はCSV列には存在しないため、ROGII loader / adapter でファイル名から付与する。
- fold manifest では `well_id` の train/valid overlap が 0 であることを検査する。

P0-2 引き渡し:

- Notebook-only, internet disabled, 9h のため、Kaggle package kernel が必須。
- `sample_submission.csv` を正本にし、`id` の well hash と row index から推論対象行を復元する。
- Vertex は探索・学習高速化に使うが、提出時は Kaggle Notebook 上で再現可能な推論経路を確保する。
- 公開/合理アクセス可能でない外部 artifact 依存は避ける。

## 実験記録

| run_id | モデル | CV Score | 変更内容 | 備考 |
|---|---|---:|---|---|
| rogii_adapter_smoke | LGBM | 184.86839178738845 | directory adapter smoke | `data.train_row_limit=200000`、1 fold smoke。提出可能性確認用 |

## 提出記録

| 日付 | run_id | CV Score | Public LB | 備考 |
|---|---|---:|---:|---|
|  |  |  |  | 初提出前 |

## 実装済み adapter

- `src/competitions/rogii.py` が `train/*.csv` / `test/*.csv` / `sample_submission.csv` から tabular runner 入力を生成する。
- train は `TVT_input` が NaN の target zone だけを使い、`TVT` を目的変数にする。
- test は `sample_submission.csv` の `id` 順を正本にし、`id`, `well_id`, `row_index` を生成する。
- `cv.group_col: well_id` により同一wellがtrain/validにまたがらない。
- `submission_target: tvt` により、学習target `TVT` と提出列 `tvt` のズレを吸収する。
- `make package-kernel CONFIG=configs/rogii_lgbm_baseline.yaml RUN_ID=rogii_adapter_smoke` で生成した推論scriptは、ローカル隔離実行で runner 出力submissionと完全一致済み。

## 調査コマンド

```bash
doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$ML_KAGGLE_TOKEN" .venv/bin/python -m kaggle competitions pages rogii-wellbore-geology-prediction --page-name Evaluation --content'
doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$ML_KAGGLE_TOKEN" .venv/bin/python -m kaggle competitions pages rogii-wellbore-geology-prediction --page-name "Code Requirements" --content'
doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$ML_KAGGLE_TOKEN" .venv/bin/python -m kaggle competitions pages rogii-wellbore-geology-prediction --page-name Timeline --content'
doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$ML_KAGGLE_TOKEN" .venv/bin/python -m kaggle competitions pages rogii-wellbore-geology-prediction --page-name data-description --content'
doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$ML_KAGGLE_TOKEN" .venv/bin/python -m kaggle competitions pages rogii-wellbore-geology-prediction --page-name rules --content'
```
