"""モデル評価メトリクスと最適化方向。全モデルで共用する。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from sklearn.metrics import log_loss, mean_squared_error, roc_auc_score


ScoreFn = Callable[[np.ndarray, np.ndarray], float]


@dataclass(frozen=True)
class MetricSpec:
    name: str
    higher_is_better: bool
    scorer: ScoreFn | None = None

    @property
    def direction(self) -> str:
        return "maximize" if self.higher_is_better else "minimize"


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def _auc(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(roc_auc_score(y_true, y_pred))


def _logloss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(log_loss(y_true, y_pred))


METRICS: dict[str, MetricSpec] = {
    "rmse": MetricSpec("rmse", higher_is_better=False, scorer=_rmse),
    "rmsle": MetricSpec("rmsle", higher_is_better=False),
    "mae": MetricSpec("mae", higher_is_better=False),
    "mape": MetricSpec("mape", higher_is_better=False),
    "logloss": MetricSpec("logloss", higher_is_better=False, scorer=_logloss),
    "multi_logloss": MetricSpec("multi_logloss", higher_is_better=False, scorer=_logloss),
    "auc": MetricSpec("auc", higher_is_better=True, scorer=_auc),
    "accuracy": MetricSpec("accuracy", higher_is_better=True),
    "f1": MetricSpec("f1", higher_is_better=True),
    "map": MetricSpec("map", higher_is_better=True),
    "ndcg": MetricSpec("ndcg", higher_is_better=True),
    "qwk": MetricSpec("qwk", higher_is_better=True),
}


def metric_spec(metric: str) -> MetricSpec:
    key = metric.lower().replace("-", "_")
    if key not in METRICS:
        raise ValueError(f"未対応の metric: {metric}")
    return METRICS[key]


def metric_is_higher_better(metric: str) -> bool:
    return metric_spec(metric).higher_is_better


def metric_direction(metric: str) -> str:
    return metric_spec(metric).direction


def higher_is_better_metric_names() -> tuple[str, ...]:
    return tuple(name for name, spec in METRICS.items() if spec.higher_is_better)


def cv_score(y_true: np.ndarray, y_pred: np.ndarray, metric: str | None = None) -> float:
    if metric is None:
        from config import METRIC

        metric = METRIC
    spec = metric_spec(metric)
    if spec.scorer is None:
        raise ValueError(f"metric は方向のみ登録済みで scorer 未実装: {metric}")
    return spec.scorer(y_true, y_pred)
