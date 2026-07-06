"""CV split helpers shared by model trainers and run artifact manifests."""
from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.model_selection import GroupKFold, KFold, StratifiedKFold


def resolve_strategy(strategy: str | None, objective: str) -> str:
    if strategy:
        return strategy
    return "kfold" if objective == "regression" else "stratified"


def make_splits(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    objective: str,
    strategy: str | None,
    n_folds: int,
    seed: int,
    groups: pd.Series | None = None,
) -> list[tuple[Any, Any]]:
    strategy = resolve_strategy(strategy, objective)
    if strategy == "kfold":
        return list(KFold(n_splits=n_folds, shuffle=True, random_state=seed).split(X))
    if strategy == "stratified":
        return list(StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed).split(X, y))
    if strategy == "group":
        if groups is None:
            raise ValueError("cv.strategy=group requires cv.group_col")
        _validate_groups(groups, n_folds=n_folds)
        return list(GroupKFold(n_splits=n_folds).split(X, y, groups=groups))
    raise ValueError(f"unsupported cv.strategy: {strategy}")


def group_overlap_report(
    splits: list[tuple[Any, Any]],
    groups: pd.Series | None,
) -> dict[str, Any] | None:
    if groups is None:
        return None
    fold_groups = []
    for fold, (_, valid_idx) in enumerate(splits):
        values = set(map(str, groups.iloc[valid_idx].dropna().unique().tolist()))
        fold_groups.append({"fold": fold, "n_groups": len(values), "groups": values})
    overlaps: list[dict[str, Any]] = []
    for left in range(len(fold_groups)):
        for right in range(left + 1, len(fold_groups)):
            overlap = sorted(fold_groups[left]["groups"] & fold_groups[right]["groups"])
            if overlap:
                overlaps.append({
                    "fold_a": left,
                    "fold_b": right,
                    "n_overlap": len(overlap),
                    "sample": overlap[:10],
                })
    return {
        "fold_group_counts": [
            {"fold": item["fold"], "n_groups": item["n_groups"]}
            for item in fold_groups
        ],
        "overlap_count": sum(item["n_overlap"] for item in overlaps),
        "overlaps": overlaps,
    }


def _validate_groups(groups: pd.Series, *, n_folds: int) -> None:
    if groups.isna().any():
        nulls = int(groups.isna().sum())
        raise ValueError(f"cv.group_col contains {nulls} null values")
    n_groups = int(groups.nunique())
    if n_groups < n_folds:
        raise ValueError(f"cv.group_col has {n_groups} groups, fewer than n_folds={n_folds}")
