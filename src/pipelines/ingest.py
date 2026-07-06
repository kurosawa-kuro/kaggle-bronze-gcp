"""Bronze → Silver: データロードと基本エンコーディング。
Kaggle コンペ転用時は load_data() だけ差し替える。
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from config import DATA_INTERIM, DATA_RAW, TARGET


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(train_df, test_df) を返す。

    1. data/<comp>/interim/train.parquet があれば即返す（キャッシュ）
    2. data/<comp>/raw/train.csv があれば Kaggle CSV モード
    3. いずれもなければ California Housing（練習用）
    """
    if (DATA_INTERIM / "train.parquet").exists():
        return (
            pd.read_parquet(DATA_INTERIM / "train.parquet"),
            pd.read_parquet(DATA_INTERIM / "test.parquet"),
        )

    if (DATA_RAW / "train.csv").exists():
        return _load_from_csv()

    return _load_california_housing()


def _load_from_csv() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Kaggle コンペモード: data/<comp>/raw/train.csv を読む"""
    train_df = pd.read_csv(DATA_RAW / "train.csv")
    test_df = pd.read_csv(DATA_RAW / "test.csv")
    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    train_df.to_parquet(DATA_INTERIM / "train.parquet", index=False)
    test_df.to_parquet(DATA_INTERIM / "test.parquet", index=False)
    print(f"[ingest] Kaggle CSV: train={len(train_df)}  test={len(test_df)}")
    return train_df, test_df


def _load_california_housing() -> tuple[pd.DataFrame, pd.DataFrame]:
    from sklearn.datasets import fetch_california_housing
    from sklearn.model_selection import train_test_split

    data = fetch_california_housing(as_frame=True)
    df = data.frame
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    test_df = test_df.drop(columns=[TARGET])

    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    train_df.to_parquet(DATA_INTERIM / "train.parquet", index=False)
    test_df.to_parquet(DATA_INTERIM / "test.parquet", index=False)
    print(f"[ingest] California Housing: train={len(train_df)}  test={len(test_df)}")
    return train_df, test_df


def encode(
    X_train: pd.DataFrame, X_test: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """null 埋め + OrdinalEncoding。fit は学習データのみ（リーク防止）。"""
    state = fit_preprocessor(X_train)
    return apply_preprocessor(X_train, state), apply_preprocessor(X_test, state)


def fit_preprocessor(X_train: pd.DataFrame) -> dict:
    """学習データだけから推論再現に必要な前処理状態を作る。"""
    cat_cols = X_train.select_dtypes(exclude=np.number).columns.tolist()
    num_cols = X_train.select_dtypes(include=np.number).columns.tolist()

    filled = X_train.copy()
    medians: dict[str, float | None] = {}
    for col in num_cols:
        med = filled[col].median()
        medians[col] = None if pd.isna(med) else float(med)
        filled[col] = filled[col].fillna(med)

    for col in cat_cols:
        filled[col] = filled[col].fillna("__missing__")

    categories: dict[str, list] = {}
    if cat_cols:
        enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        enc.fit(filled[cat_cols])
        categories = {
            col: [_json_scalar(v) for v in cats.tolist()]
            for col, cats in zip(cat_cols, enc.categories_, strict=True)
        }

    return {
        "version": 1,
        "numeric_cols": list(map(str, num_cols)),
        "categorical_cols": list(map(str, cat_cols)),
        "feature_names_in": list(map(str, X_train.columns)),
        "numeric_medians": medians,
        "categorical_categories": categories,
        "unknown_category_value": -1,
        "missing_category_value": "__missing__",
    }


def apply_preprocessor(X: pd.DataFrame, state: dict) -> pd.DataFrame:
    """保存済み前処理状態で特徴量を変換する。未知カテゴリは -1。"""
    out = X.copy()
    feature_names = state["feature_names_in"]
    missing = [col for col in feature_names if col not in out.columns]
    if missing:
        raise ValueError(f"missing feature columns for preprocessing: {missing[:5]}")
    out = out[feature_names]

    for col in state.get("numeric_cols", []):
        med = state.get("numeric_medians", {}).get(col)
        if med is not None:
            out[col] = out[col].fillna(med)

    missing_value = state.get("missing_category_value", "__missing__")
    unknown_value = state.get("unknown_category_value", -1)
    for col in state.get("categorical_cols", []):
        categories = state.get("categorical_categories", {}).get(col, [])
        mapping = {value: idx for idx, value in enumerate(categories)}
        out[col] = out[col].fillna(missing_value).map(mapping).fillna(unknown_value).astype(float)

    return out


def _json_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    return value
