# 07 テスト戦略

## 方針

Kaggle パイプラインはノートブックファーストで速く回すことが優先。  
ユニットテストは最小限にとどめ、通常開発では **`make smoke` が通ること**を最低品質ゲートとする。GCP 経路を触った場合は Vertex Custom Job / BigQuery / GCS 回収まで確認し、推論コンテナや Model Registry を触った場合は Vertex Batch Prediction まで確認する。

## 品質ゲート

```bash
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=smoke_check
make logs
make compare
```

GCP 経路を変更した場合:

```bash
make stage-data
make build-push
make train-vertex CONFIG=configs/lgbm_baseline.yaml RUN_ID=<run_id>
make collect CONFIG=configs/lgbm_baseline.yaml RUN_ID=<run_id>
make cost-record CONFIG=configs/lgbm_baseline.yaml RUN_ID=<run_id>
make compare RUN_LIKE='<run_id>%' LIMIT=20
```

推論経路を変更した場合:

```bash
make build-push-serving
make batch-input CONFIG=configs/lgbm_baseline.yaml RUN_ID=<run_id>
make register-servable CONFIG=configs/lgbm_baseline.yaml RUN_ID=<run_id>
make batch-predict CONFIG=configs/lgbm_baseline.yaml RUN_ID=<run_id> SRC=gs://<bucket>/batch_input/<comp>/<run_id>/instances.jsonl
```

## CV スコアによる品質判断

| 判断基準 | 目安 |
|---|---|
| CV std が安定している | `std < 0.015` を目安（不安定なら fold 数や seed を確認）|
| CV Score が改善している | 前回 run_id との比較で改善が確認できること |
| Public LB との乖離が小さい | `\|CV - LB\| < 0.05` を目安。大きい場合はリークを疑う |

## テスト範囲

| 範囲 | 手段 | 備考 |
|---|---|---|
| パイプライン結合 | `make smoke` | エラーなく完了し、run_id 成果物が生成されること |
| モデル切り替え | `make nb NB=exp002_catboost_base` | 同様にエラーなく完了すること |
| 実験ログ記録 | `make logs` | run_id と cv_score が記録されていること |
| FE 追加 | `make run` 後に CV Score を比較 | スコアが改善または維持されること |
| GCP 訓練・評価 | `make train-vertex` + `make collect` + `make compare` | Vertex job が `JOB_STATE_SUCCEEDED`、BQ と成果物が揃うこと |
| GCP 推論 | `make batch-predict` | Batch Prediction が `JOB_STATE_SUCCEEDED`、`successful_count` が test 件数と一致すること |

## 実証済み E2E ベースライン

2026-07-06 に `full_gcp_lgbm_001` で GCP フル検証済み。

- Vertex Custom Job: `projects/941178142366/locations/us-central1/customJobs/5462847664892674048`
- CV: `0.08668087872662794`
- Vertex Batch Prediction: `projects/941178142366/locations/us-central1/batchPredictionJobs/8231488312376819712`
- Batch successful_count: `247435`

## タスク完了条件

各 task は、完了前に以下を `Verification` に残す:

- 実行したコマンドと出力（CV Score）
- 前回との比較
- 実行できなかった検証と理由
- 残るリスク（Public LB との乖離等）

## Fold リーク検査

FE を追加した後、CV Score が不自然に高くなった場合はリークを疑う:

```python
# 検査: train と test で分布が揃っているか
print(X_train["new_feature"].describe())
print(X_test["new_feature"].describe())
```

## 関連タスク

- テスト追加や期待値変更が必要な場合は、task に理由を書き、仕様変更なら先に該当 docs を更新する。
