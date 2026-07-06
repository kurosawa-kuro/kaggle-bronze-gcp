# 08 提出 Runbook

Kaggle における「リリース」= 最終提出ファイルの選択と提出。現行の正規経路は run_id 成果物から `make submit` すること。

## 提出前チェックリスト

```bash
make logs
find outputs/runs/<competition>/<run_id> -maxdepth 1 -type f -printf '%f\n' | sort
head outputs/runs/<competition>/<run_id>/submission.csv
wc -l outputs/runs/<competition>/<run_id>/submission.csv
```

確認項目:

- [ ] `submission.csv` のヘッダがコンペ規定と一致している
- [ ] 行数がテストデータの行数と一致している
- [ ] 値に NaN / inf が含まれていない
- [ ] `metrics.json` と BigQuery `kaggle_ops.experiments` の run_id / score が対応している
- [ ] Vertex 実行の場合は `make collect CONFIG=<cfg> RUN_ID=<id>` 済み
- [ ] Vertex 実行の場合は必要に応じて `make cost-record CONFIG=<cfg> RUN_ID=<id>` 済み

## 最終提出の選択（2本戦略）

Kaggle は締切までに 2 本の提出を選択できる（デフォルトは最終 2 提出）。

| 提出 | 選び方 |
|---|---|
| 提出 A | CV Score が最良の run_id（`make logs` / BigQuery で確認） |
| 提出 B | Public LB Score が最良の run_id |

両者が同じなら 1 本で問題ない。

## Kaggle CLI での提出

```bash
make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001_lgbm MSG="exp001: lgbm baseline CV=0.44498"
```

旧 root `submission.csv` を直接出す場合だけ:

```bash
make submit-legacy COMP=<competition-name> MSG="legacy submission"
```

## コンペ切り替え手順

```bash
make init COMP=<competition-slug>
vim env/config.yaml
cp env/config.yaml configs/<competition>_lgbm_baseline.yaml
rm -rf data/<competition>/interim data/<competition>/features
make smoke CONFIG=configs/<competition>_lgbm_baseline.yaml RUN_ID=smoke01
```

Vertex へ投げる場合:

```bash
make stage-data
make build-push
make train-vertex CONFIG=configs/<competition>_lgbm_baseline.yaml RUN_ID=exp001
make collect CONFIG=configs/<competition>_lgbm_baseline.yaml RUN_ID=exp001
```

## GCP リソース後始末

通常の Custom Job / Batch Prediction は完了後に常駐しない。Endpoint だけは常駐コストがあるため、使った場合は必ず削除する。

```bash
make endpoint-teardown CONFIG=configs/lgbm_baseline.yaml
make cost
```

## ロールバック（前の実験に戻す）

過去 run_id の成果物を提出し直す。

```bash
make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=<previous_run_id> MSG="rollback to previous run"
```

local に成果物がなければ先に回収する。

```bash
make collect CONFIG=configs/lgbm_baseline.yaml RUN_ID=<previous_run_id>
```

## 提出後タスク

- Public LB スコアと CV Score の差を `docs/tasks/active/` に記録する。
- 乖離が大きい場合（`|CV - LB| > 0.05`）は原因を調査してリーク防止策を `docs/06_error_policy.md` に追記する。
- 結果（ブロンズ取得 / 未達）と振り返りを task に残す。
