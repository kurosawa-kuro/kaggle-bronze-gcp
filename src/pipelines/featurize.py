"""Silver → Gold: 特徴量エンジニアリングのエントリポイント。"""
import os
from pathlib import Path

import pandas as pd
import yaml
from sklearn.preprocessing import LabelEncoder

from config import ID_COL, TARGET
from features import apply_feature_registry
from pipelines.ingest import apply_preprocessor, fit_preprocessor

# multiclass 時に make_features() が設定する。score.py が参照して class 名に戻す。
LABEL_CLASSES: list[str] | None = None


def make_features(
    train_df: pd.DataFrame, test_df: pd.DataFrame, *, return_preprocess_state: bool = False
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame] | tuple[pd.DataFrame, pd.Series, pd.DataFrame, dict]:
    """X_train, y_train, X_test を返す。"""
    global LABEL_CLASSES

    y_train = train_df[TARGET]
    X_train = train_df.drop(columns=[TARGET])
    X_test = test_df.copy()

    # ID列は予測に不要なため除外（submission では original_test から取得）
    for col in [ID_COL]:
        if col and col in X_train.columns:
            X_train = X_train.drop(columns=[col])
        if col and col in X_test.columns:
            X_test = X_test.drop(columns=[col])

    X_train, X_test = apply_feature_registry(X_train, X_test, _configured_features())

    # 文字列ターゲット（multiclass）はラベルエンコードして整数に変換する
    if not pd.api.types.is_numeric_dtype(y_train):
        le = LabelEncoder()
        y_train = pd.Series(le.fit_transform(y_train), index=y_train.index, name=TARGET)
        LABEL_CLASSES = le.classes_.tolist()
    else:
        LABEL_CLASSES = None

    preprocess_state = fit_preprocessor(X_train)
    X_train = apply_preprocessor(X_train, preprocess_state)
    X_test = apply_preprocessor(X_test, preprocess_state)
    preprocess_state["target"] = TARGET
    preprocess_state["id_col"] = ID_COL
    preprocess_state["label_classes"] = LABEL_CLASSES
    if return_preprocess_state:
        return X_train, y_train, X_test, preprocess_state
    return X_train, y_train, X_test


def _configured_features() -> list[str]:
    path = Path(os.environ.get("KBC_CONFIG_PATH", "env/config.yaml"))
    if not path.exists():
        return ["base"]
    cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    names = cfg.get("features")
    if names is None:
        names = cfg.get("feature_sets")
    if names is None:
        return ["base"]
    if isinstance(names, str):
        return [names]
    return list(names)
