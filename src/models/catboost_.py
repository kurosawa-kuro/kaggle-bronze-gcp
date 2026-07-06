"""CatBoost train_cv() with the same runner contract as models.lgbm."""

import numpy as np

from config import METRIC, N_FOLDS, OBJECTIVE, SEED
from pipelines.evaluate import cv_score
from pipelines.splits import make_splits
from utils.logger import log_run

_LOSS_MAP = {
    "regression": "RMSE",
    "binary": "Logloss",
    "multiclass": "MultiClass",
}


def train_cv(
    X_train,
    y_train,
    params: dict | None = None,
    notes: str = "",
    *,
    n_folds: int | None = None,
    seed: int | None = None,
    max_folds: int | None = None,
    num_boost_round: int = 2000,
    early_stopping_rounds: int = 50,
    log_run_id: str | None = None,
    cv_strategy: str | None = None,
    groups=None,
) -> tuple[np.ndarray, list]:
    from catboost import CatBoostClassifier, CatBoostRegressor

    seed = int(seed if seed is not None else SEED)
    n_folds = int(n_folds if n_folds is not None else N_FOLDS)
    base_params = {
        "iterations": num_boost_round,
        "learning_rate": 0.05,
        "depth": 6,
        "early_stopping_rounds": early_stopping_rounds,
        "random_seed": seed,
        "verbose": 200,
        "allow_writing_files": False,
    }
    merged = {**base_params, **(params or {})}

    loss_fn = _LOSS_MAP[OBJECTIVE]
    ModelCls = CatBoostRegressor if OBJECTIVE == "regression" else CatBoostClassifier

    splits = make_splits(
        X_train,
        y_train,
        objective=OBJECTIVE,
        strategy=cv_strategy,
        n_folds=n_folds,
        seed=seed,
        groups=groups,
    )
    if max_folds is not None:
        splits = splits[:max_folds]
    n_classes = int(y_train.nunique()) if OBJECTIVE == "multiclass" else 1
    oof = np.zeros((len(y_train), n_classes)) if n_classes > 1 else np.zeros(len(y_train))
    models = []
    fold_scores: list[float] = []

    for fold, (tr_idx, val_idx) in enumerate(splits):
        X_tr, X_val = X_train.iloc[tr_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[tr_idx], y_train.iloc[val_idx]

        model = ModelCls(loss_function=loss_fn, **merged)
        model.fit(X_tr, y_tr, eval_set=(X_val, y_val))
        models.append(model)

        # multiclass は predict_proba で確率を取得（log_loss に必要）
        if OBJECTIVE == "multiclass":
            oof[val_idx] = model.predict_proba(X_val)
        elif OBJECTIVE == "binary":
            oof[val_idx] = model.predict_proba(X_val)[:, 1]
        else:
            oof[val_idx] = model.predict(X_val).flatten()

        score = cv_score(y_val.values, oof[val_idx])
        fold_scores.append(score)
        print(f"  [catboost] fold {fold + 1}/{len(splits)}  {METRIC}={score:.5f}")

    _log(fold_scores, merged, notes, log_run_id=log_run_id)
    return oof, models


def _log(fold_scores, params, notes, *, log_run_id: str | None):
    mean = float(np.mean(fold_scores))
    std = float(np.std(fold_scores))
    print(f"\n[catboost] CV {METRIC} = {mean:.5f}  (std={std:.5f})")
    run_id = log_run_id or "catboost_cv"
    log_run(run_id=run_id, cv_score=mean, params=params, notes=notes)
