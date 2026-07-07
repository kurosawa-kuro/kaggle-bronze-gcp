"""推論・提出ファイル生成（スコアリングパイプライン）。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import pipelines.featurize as _featurize

from config import DATA_RAW, ID_COL, OBJECTIVE, SUBMISSION_TARGET, TARGET


def predict(X_test: pd.DataFrame, models: list) -> np.ndarray:
    """全 fold モデルの平均予測を返す。multiclass は (n_test, n_classes) を返す。"""
    return np.mean([m.predict(X_test) for m in models], axis=0)


def make_submission(
    X_test: pd.DataFrame,
    models: list,
    out_path: str | Path = "submission.csv",
    original_test: pd.DataFrame | None = None,
) -> pd.DataFrame:
    preds = predict(X_test, models)

    sub = write_submission_from_predictions(
        Path(out_path),
        preds,
        cfg={
            "data": {
                "id_col": ID_COL,
                "objective": OBJECTIVE,
                "target": TARGET,
                "submission_target": SUBMISSION_TARGET,
                "raw_dir": str(DATA_RAW),
            }
        },
        original_test=original_test if original_test is not None else X_test,
        label_classes=_featurize.LABEL_CLASSES,
    )
    print(f"[score] submission saved → {out_path}  shape={sub.shape}")
    return sub


def write_submission_from_predictions(
    out_path: Path,
    preds: np.ndarray,
    *,
    cfg: dict[str, Any],
    original_test: pd.DataFrame,
    label_classes: list[str] | None = None,
    contract_path: Path | None = None,
    sample_path: Path | None = None,
) -> pd.DataFrame:
    """Write submission.csv using sample_submission.csv as the contract when present."""
    data_cfg = cfg.get("data", cfg)
    sample_path = sample_path or sample_submission_path(cfg)
    sample = pd.read_csv(sample_path) if sample_path and sample_path.exists() else None
    sub, contract = build_submission_frame(
        preds,
        cfg=cfg,
        original_test=original_test,
        label_classes=label_classes,
        sample=sample,
        sample_path=sample_path if sample is not None else None,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sub.to_csv(out_path, index=False)
    contract["output_path"] = str(out_path)
    contract["competition"] = data_cfg.get("comp") or data_cfg.get("slug")
    if contract_path is None:
        contract_path = out_path.with_name("submission_contract.json")
    contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
    return sub


def build_submission_frame(
    preds: np.ndarray,
    *,
    cfg: dict[str, Any],
    original_test: pd.DataFrame,
    label_classes: list[str] | None = None,
    sample: pd.DataFrame | None = None,
    sample_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    data_cfg = cfg.get("data", cfg)
    objective = data_cfg.get("objective")
    target_col = data_cfg.get("submission_target") or data_cfg.get("target", "target")
    id_col = data_cfg.get("id_col")
    values = prediction_values(preds, objective=objective, label_classes=label_classes)

    if sample is not None:
        if len(sample) != len(values):
            raise ValueError(f"sample_submission row count mismatch: sample={len(sample)} preds={len(values)}")
        sub = sample.copy()
        target_cols = _sample_target_columns(sample, id_col=id_col, fallback_target=target_col)
        _assign_target_values(sub, target_cols=target_cols, values=values)
        fallback = False
    else:
        target_cols = [target_col]
        payload: dict[str, Any] = {target_col: values}
        if id_col and id_col in original_test.columns:
            payload = {id_col: original_test[id_col].to_numpy(), **payload}
        sub = pd.DataFrame(payload)
        fallback = True

    contract = {
        "version": 1,
        "fallback": fallback,
        "sample_path": str(sample_path) if sample_path else None,
        "sample_sha256": _sha256(sample_path) if sample_path else None,
        "columns": list(map(str, sub.columns)),
        "row_count": int(len(sub)),
        "target_columns": list(map(str, target_cols)),
        "id_col": id_col,
        "objective": objective,
    }
    return sub, contract


def prediction_values(preds: np.ndarray, *, objective: str | None, label_classes: list[str] | None = None) -> np.ndarray:
    arr = np.asarray(preds)
    if objective == "multiclass" and arr.ndim > 1:
        labels = label_classes or [str(i) for i in range(arr.shape[1])]
        return np.asarray([labels[int(i)] for i in np.argmax(arr, axis=1)])
    return arr


def sample_submission_path(cfg: dict[str, Any]) -> Path | None:
    data_cfg = cfg.get("data", cfg)
    explicit = data_cfg.get("sample_submission") or data_cfg.get("sample_submission_path")
    if explicit:
        return Path(explicit)
    raw_dir = data_cfg.get("raw_dir")
    if raw_dir:
        path = Path(raw_dir) / "sample_submission.csv"
        return path if path.exists() else None
    path = DATA_RAW / "sample_submission.csv"
    return path if path.exists() else None


def _sample_target_columns(sample: pd.DataFrame, *, id_col: str | None, fallback_target: str) -> list[str]:
    if id_col and id_col in sample.columns:
        cols = [col for col in sample.columns if col != id_col]
    elif fallback_target in sample.columns:
        cols = [fallback_target]
    else:
        cols = list(sample.columns[1:]) if len(sample.columns) > 1 else list(sample.columns)
    if not cols:
        raise ValueError("sample_submission has no target columns")
    return cols


def _assign_target_values(sub: pd.DataFrame, *, target_cols: list[str], values: np.ndarray) -> None:
    arr = np.asarray(values)
    if len(target_cols) == 1:
        sub[target_cols[0]] = arr
        return
    if arr.ndim != 2 or arr.shape[1] != len(target_cols):
        raise ValueError(
            f"prediction shape does not match sample target columns: preds={arr.shape} targets={len(target_cols)}"
        )
    for idx, col in enumerate(target_cols):
        sub[col] = arr[:, idx]


def _sha256(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
