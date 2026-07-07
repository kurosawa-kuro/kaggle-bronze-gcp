"""Feature engineering registry."""
from __future__ import annotations

from typing import Callable

import pandas as pd

FeatureFn = Callable[[pd.DataFrame, pd.DataFrame], tuple[pd.DataFrame, pd.DataFrame]]


def base_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return X_train, X_test


def stellar_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    from features.stellar import add_stellar_fe

    return add_stellar_fe(X_train, X_test)


FEATURE_REGISTRY: dict[str, FeatureFn] = {
    "base": base_features,
    "stellar": stellar_features,
}


def apply_feature_registry(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    feature_names: list[str] | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    names = feature_names or ["base"]
    for name in names:
        if name not in FEATURE_REGISTRY:
            raise ValueError(f"unknown feature set: {name}")
        X_train, X_test = FEATURE_REGISTRY[name](X_train.copy(), X_test.copy())
    return X_train, X_test
