# grep: high_risk_ops

evidence_id: ev.grep.high_risk_ops
description: delete / drop / truncate / migration

- src/features/stellar.py:L20: df["redshift_bin"] = pd.qcut(df["redshift"], q=10, labels=False, duplicates="drop")
- src/pipelines/featurize.py:L21: X_train = train_df.drop(columns=[TARGET])
- src/pipelines/featurize.py:L27: X_train = X_train.drop(columns=[col])
- src/pipelines/featurize.py:L29: X_test = X_test.drop(columns=[col])
- src/pipelines/ingest.py:L48: test_df = test_df.drop(columns=[TARGET])
- src/runner/experiment/train.py:L76: tmp = tempfile.NamedTemporaryFile("wb", suffix=".yaml", delete=False)
- src/runner/model/deploy.py:L94: ep.delete(force=True)
- src/runner/model/register.py:L173: tmp = tempfile.NamedTemporaryFile("wb", suffix=".yaml", delete=False)
- src/utils/artifact_store.py:L17: path = uri.removeprefix("gs://").strip("/")
- src/utils/artifact_store.py:L69: blob.name.removeprefix(prefix).split("/", 1)[0]
- src/utils/artifact_store.py:L71: if blob.name.removeprefix(prefix).split("/", 1)[0]
