# Controlled Code Excerpts

evidence_id: ev.code_excerpts.summary

Small deterministic source excerpts around public/test anchors. This is controlled raw evidence for investigation; it is not a license to read or paste the full repository.

## infra/Dockerfile:1-4 `python:3.12-slim`

language: `dockerfile`

```text
1: FROM python:3.12-slim
2: 
3: # libgomp1: OpenMP runtime required by LightGBM / XGBoost (absent in slim image)
4: RUN apt-get update \
```

## notebooks/optuna_lgbm.py:35-41 `objective`

language: `python`

```text
35: }
36: 
37: 
38: def objective(trial: optuna.Trial) -> float:
39:     params = {
40:         **BASE_PARAMS,
41:         "num_leaves": trial.suggest_int("num_leaves", 31, 255),
```

## scripts/init_competition.py:76-82 `analyze`

language: `python`

```text
76:     return dst_train, dst_test
77: 
78: 
79: def analyze(train_path: Path, test_path: Path) -> None:
80:     print("\n[init] ③ データ分析中 ...")
81:     train = pd.read_csv(train_path)
82:     test = pd.read_csv(test_path) if test_path.exists() else None
```

## scripts/init_competition.py:130-136 `create_doc`

language: `python`

```text
130:     print("  ──────────────────────────────────────────────────────")
131: 
132: 
133: def create_doc(comp: str) -> None:
134:     print("\n[init] ④ コンペドキュメントを生成中 ...")
135:     template = ROOT / "docs" / "competitions" / "_template.md"
136:     dest = ROOT / "docs" / "competitions" / f"{comp}.md"
```

## scripts/init_competition.py:17-23 `download`

language: `python`

```text
17: KAGGLE_BIN = Path(sys.executable).parent / "kaggle"
18: 
19: 
20: def download(comp: str, raw_dir: Path) -> None:
21:     print(f"[init] ① {comp} をダウンロード中 ...")
22:     result = subprocess.run(
23:         [str(KAGGLE_BIN), "competitions", "download",
```

## scripts/init_competition.py:144-150 `main`

language: `python`

```text
144:     print(f"  作成: docs/competitions/{comp}.md")
145: 
146: 
147: def main() -> None:
148:     if len(sys.argv) < 2:
149:         print("Usage: make init COMP=<competition-slug>")
150:         sys.exit(1)
```

## scripts/init_competition.py:46-52 `normalize`

language: `python`

```text
46: <redacted sensitive-looking assignment>
47: 
48: 
49: def normalize(raw_dir: Path) -> tuple[Path, Path]:
50:     print("\n[init] ② ファイル配置を正規化中 ...")
51:     train_src = _find_csv(raw_dir, "train")
52:     test_src = _find_csv(raw_dir, "test", exclude="sample")
```

## src/features/stellar.py:3-9 `add_stellar_fe`

language: `python`

```text
3: import pandas as pd
4: 
5: 
6: def add_stellar_fe(
7:     X_train: pd.DataFrame, X_test: pd.DataFrame
8: ) -> tuple[pd.DataFrame, pd.DataFrame]:
9:     for df in (X_train, X_test):
```

## src/models/catboost_.py:16-22 `train_cv`

language: `python`

```text
16: }
17: 
18: 
19: def train_cv(
20:     X_train, y_train, params: dict | None = None, notes: str = ""
21: ) -> tuple[np.ndarray, list]:
22:     from catboost import CatBoostClassifier, CatBoostRegressor
```

## src/models/ensemble.py:2-8 `average`

language: `python`

```text
2: import numpy as np
3: 
4: 
5: def average(predictions: list[np.ndarray], weights: list[float] | None = None) -> np.ndarray:
6:     """単純平均 or 重み付き平均。"""
7:     if weights is None:
8:         return np.mean(predictions, axis=0)
```

## src/models/lgbm.py:24-30 `train_cv`

language: `python`

```text
24: }
25: 
26: 
27: def train_cv(
28:     X_train,
29:     y_train,
30:     params: dict | None = None,
```

## src/models/xgboost_.py:21-27 `train_cv`

language: `python`

```text
21: }
22: 
23: 
24: def train_cv(
25:     X_train, y_train, params: dict | None = None, notes: str = ""
26: ) -> tuple[np.ndarray, list]:
27:     import xgboost as xgb
```

## src/pipelines/evaluate.py:5-11 `cv_score`

language: `python`

```text
5: from config import METRIC
6: 
7: 
8: def cv_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
9:     if METRIC == "rmse":
10:         return float(np.sqrt(mean_squared_error(y_true, y_pred)))
11:     if METRIC == "auc":
```

## src/pipelines/featurize.py:11-17 `make_features`

language: `python`

```text
11: LABEL_CLASSES: list[str] | None = None
12: 
13: 
14: def make_features(
15:     train_df: pd.DataFrame, test_df: pd.DataFrame
16: ) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
17:     """X_train, y_train, X_test を返す。"""
```

## src/pipelines/ingest.py:54-60 `encode`

language: `python`

```text
54:     return train_df, test_df
55: 
56: 
57: def encode(
58:     X_train: pd.DataFrame, X_test: pd.DataFrame
59: ) -> tuple[pd.DataFrame, pd.DataFrame]:
60:     """null 埋め + OrdinalEncoding。fit は学習データのみ（リーク防止）。"""
```

## src/pipelines/ingest.py:8-14 `load_data`

language: `python`

```text
8: from config import DATA_INTERIM, DATA_RAW, TARGET
9: 
10: 
11: def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
12:     """(train_df, test_df) を返す。
13: 
14:     1. data/<comp>/interim/train.parquet があれば即返す（キャッシュ）
```

## src/pipelines/score.py:14-20 `make_submission`

language: `python`

```text
14:     return np.mean([m.predict(X_test) for m in models], axis=0)
15: 
16: 
17: def make_submission(
18:     X_test: pd.DataFrame,
19:     models: list,
20:     out_path: str | Path = "submission.csv",
```

## src/pipelines/score.py:9-15 `predict`

language: `python`

```text
9: from config import ID_COL, OBJECTIVE, TARGET
10: 
11: 
12: def predict(X_test: pd.DataFrame, models: list) -> np.ndarray:
13:     """全 fold モデルの平均予測を返す。multiclass は (n_test, n_classes) を返す。"""
14:     return np.mean([m.predict(X_test) for m in models], axis=0)
15: 
```

## src/ports.py:23-29 `FeatureTransformer`

language: `python`

```text
23: 
24: 
25: @runtime_checkable
26: class FeatureTransformer(Protocol):
27:     """FE 追加関数が満たすべきインタフェース。
28:     features/base.py の make_features() および features/*.add_*() はこれに適合する。
29:     呼び出し元: X_new = transformer(X)
```

## src/ports.py:8-14 `ModelTrainer`

language: `python`

```text
8: 
9: 
10: @runtime_checkable
11: class ModelTrainer(Protocol):
12:     """全モデルが満たすべきインタフェース。
13:     lgbm.py / catboost_.py / xgboost_.py はこの Protocol に適合する。
14:     """
```

## src/ports.py:13-19 `train_cv`

language: `python`

```text
13:     lgbm.py / catboost_.py / xgboost_.py はこの Protocol に適合する。
14:     """
15: 
16:     def train_cv(
17:         self,
18:         X_train: pd.DataFrame,
19:         y_train: pd.Series,
```

## src/runner/experiment/hp_tune.py:17-23 `main`

language: `python`

```text
17: METRIC_TAG = "cv_score"
18: 
19: 
20: def main(argv: list[str] | None = None) -> int:
21:     parser = argparse.ArgumentParser(description="Submit a Vertex Hyperparameter Tuning job")
22:     parser.add_argument("--config", default="configs/lgbm_baseline.yaml")
23:     parser.add_argument("--run-id", required=True)
```

## src/runner/experiment/sweep.py:12-18 `main`

language: `python`

```text
12: from runner.experiment.vertex_run import submit_from_config
13: 
14: 
15: def main(argv: list[str] | None = None) -> int:
16:     parser = argparse.ArgumentParser(description="Submit multiple configs as parallel Vertex Custom Jobs")
17:     parser.add_argument("--configs", nargs="+", required=True, help="config yaml paths")
18:     parser.add_argument("--tag", default=None, help="run_id suffix to group this sweep")
```

## src/runner/experiment/train.py:367-373 `flush`

language: `python`

```text
367:             stream.flush()
368:         return len(data)
369: 
370:     def flush(self) -> None:
371:         for stream in self.streams:
372:             stream.flush()
373: 
```

## Guardrail

- Excerpts are capped and redacted for sensitive-looking assignment lines. Confirm full context with owner approval before relying on omitted lines.
