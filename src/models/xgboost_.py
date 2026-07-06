"""XGBoost train_cv() with the same runner contract as models.lgbm."""

import numpy as np

from config import METRIC, N_FOLDS, OBJECTIVE, SEED
from pipelines.evaluate import cv_score
from pipelines.splits import make_splits
from utils.logger import log_run

_OBJECTIVE_MAP = {
    "regression": "reg:squarederror",
    "binary": "binary:logistic",
    "multiclass": "multi:softprob",
}
_METRIC_MAP = {
    "rmse": "rmse",
    "auc": "auc",
    "logloss": "logloss",
}
_MULTICLASS_METRIC_MAP = {
    "logloss": "mlogloss",
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
    import xgboost as xgb

    seed = int(seed if seed is not None else SEED)
    n_folds = int(n_folds if n_folds is not None else N_FOLDS)
    base_params = {
        "objective": _OBJECTIVE_MAP[OBJECTIVE],
        "eval_metric": _eval_metric(),
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "seed": seed,
    }
    if OBJECTIVE == "multiclass":
        base_params["num_class"] = int(y_train.nunique())
    merged = {**base_params, **(params or {})}

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

        dtrain = xgb.DMatrix(X_tr, label=y_tr)
        dval = xgb.DMatrix(X_val, label=y_val)

        model = xgb.train(
            merged,
            dtrain,
            num_boost_round=num_boost_round,
            evals=[(dval, "val")],
            early_stopping_rounds=early_stopping_rounds,
            verbose_eval=200,
        )
        pred = model.predict(dval)
        if OBJECTIVE == "multiclass":
            pred = _normalize_proba(pred)
        oof[val_idx] = pred
        models.append(model)

        score = cv_score(y_val.values, oof[val_idx])
        fold_scores.append(score)
        print(f"  [xgboost] fold {fold + 1}/{len(splits)}  {METRIC}={score:.5f}")

    _log(fold_scores, merged, notes, log_run_id=log_run_id)
    return oof, models


def _eval_metric() -> str:
    if OBJECTIVE == "multiclass":
        return _MULTICLASS_METRIC_MAP.get(METRIC, "mlogloss")
    return _METRIC_MAP.get(METRIC, "rmse")


def _normalize_proba(pred: np.ndarray) -> np.ndarray:
    pred = np.clip(np.asarray(pred, dtype=np.float64), 0.0, 1.0)
    row_sum = pred.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1.0
    return pred / row_sum


def _log(fold_scores, params, notes, *, log_run_id: str | None):
    mean = float(np.mean(fold_scores))
    std = float(np.std(fold_scores))
    print(f"\n[xgboost] CV {METRIC} = {mean:.5f}  (std={std:.5f})")
    run_id = log_run_id or "xgboost_cv"
    log_run(run_id=run_id, cv_score=mean, params=params, notes=notes)
