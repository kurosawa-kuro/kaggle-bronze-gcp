# 06 エラー方針

## エラー分類

| 分類 | 意味 | 対応 |
|---|---|---|
| **データリーク（FE）** | 学習データ全体で fit し、テストに transform した | `encode()` / `add_*()` は必ず train データのみで fit する |
| **データリーク（CV）** | Fold 外の情報を使って学習した | KFold の分割後に fit する。Target Encoding は Fold 内で必ず行う |
| **Public LB 過学習** | CV Score は良いが Private LB で大幅ダウン | CV Score を主指標にする。LB スコアに引きずられない |
| **キャッシュ不整合** | `data/<comp>/interim/` や feature cache が古いまま残っている | コンペ切り替え時は対象コンペの cache を削除してから `make smoke` |
| **設定ミスマッチ** | config の target / id_col / metric がデータに合わない | `make smoke CONFIG=<cfg>` 実行直後のエラーメッセージで確認 |
| **GCS staging 不整合** | Vertex job が古い raw data を読んでいる | `make stage-data` を再実行し、`gs://<bucket>/data/<comp>/raw/` を確認 |
| **Vertex image 不整合** | `src/` や依存変更後に古い image で Vertex 実行している | `make build-push` を再実行する。config 変更だけなら rebuild 不要 |
| **Endpoint 放置** | Vertex Endpoint が課金され続ける | 使用後すぐ `make endpoint-teardown`、月次は `make cost` で確認 |
| **パッケージ欠損** | venv にライブラリが入っていない | `make setup` を再実行する |

## Fold リーク防止の規則

```python
# NG: 学習データ全体で fit してから fold 分割
enc.fit(X_train_all)
for fold in folds:
    X_tr = enc.transform(X_tr)   # ← リーク

# OK: fold 内で fit
for fold in folds:
    enc.fit(X_tr)
    X_tr  = enc.transform(X_tr)
    X_val = enc.transform(X_val)  # ← fit は学習 fold のみ
```

Target Encoding を使う場合は必ず `category_encoders.TargetEncoder` を fold 内で fit する。

## ログ

- `[ingest]`, `[lgbm]`, `[catboost]`, `[xgboost]`, `[logger]`, `[score]` プレフィックスで標準出力に出る。
- 秘密情報（API トークン等）をログに出さない。
- 実験ログは BigQuery `<bqDataset>.experiments` に永続化される（`make logs` で確認）。
- コストログは BigQuery `kaggle_ops.cost_estimates` に永続化される（`make cost-record` / `make cost`）。

## 関連タスク

- リーク・スコア異常は task に再現手順と原因を残してから修正する。
- 障害対応で得た恒久手順は `docs/runbooks/` へ昇格する。
