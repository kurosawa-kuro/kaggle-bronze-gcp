"""Blend OOF/test predictions from compatible experiment runs."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from pipelines.evaluate import metric_is_higher_better


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blend compatible run artifacts")
    parser.add_argument("--config", default="configs/lgbm_baseline.yaml")
    parser.add_argument("--run-ids", nargs="+", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        blend(
            config_path=Path(args.config),
            run_ids=args.run_ids,
            run_id=args.run_id,
            output_root=Path(args.output_root) if args.output_root else None,
        )
    except Exception:
        import traceback

        traceback.print_exc()
        return 1
    return 0


def blend(*, config_path: Path, run_ids: list[str], run_id: str, output_root: Path | None = None) -> Path:
    config_path = config_path.resolve()
    os.environ["KBC_CONFIG_PATH"] = str(config_path)

    from pipelines.evaluate import cv_score

    cfg = _load_yaml(config_path)
    data_cfg = cfg.get("data", cfg)
    competition = data_cfg["comp"]
    output_root = output_root or Path(cfg.get("runtime", {}).get("output_root", "outputs/runs"))
    source_dirs = [output_root / competition / source for source in run_ids]
    for source_dir in source_dirs:
        if not source_dir.exists():
            raise FileNotFoundError(f"source run not found: {source_dir}")

    _assert_compatible_manifests(source_dirs)
    oofs = [_read_prediction_frame(path / "oof.parquet", required_target=True) for path in source_dirs]
    tests = [_read_prediction_frame(path / "test_pred.parquet", required_target=False) for path in source_dirs]
    y_true = oofs[0]["target"].to_numpy()
    trained = oofs[0]["trained"].to_numpy(dtype=bool)
    for oof in oofs[1:]:
        if not np.array_equal(oof["target"].to_numpy(), y_true):
            raise ValueError("OOF target order differs between source runs")
        if not np.array_equal(oof["trained"].to_numpy(dtype=bool), trained):
            raise ValueError("OOF trained mask differs between source runs")

    oof_preds = [item["pred"] for item in oofs]
    test_preds = [item["pred"] for item in tests]
    candidates = _blend_candidates(oof_preds, test_preds)
    scored = []
    for candidate in candidates:
        score = cv_score(y_true[trained], candidate["oof"][trained])
        scored.append({**candidate, "cv_score": float(score)})
    best = _choose_best(scored, metric=data_cfg["metric"])

    run_dir = output_root / competition / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, run_dir / "config.yaml")
    _write_prediction_frame(run_dir / "oof.parquet", best["oof"], target=y_true, trained=trained)
    _write_prediction_frame(run_dir / "test_pred.parquet", best["test"])
    _write_submission(run_dir / "submission.csv", best["test"], cfg=cfg, source_dir=source_dirs[0])
    _write_blend_manifest(run_dir / "fold_manifest.json", source_dirs=source_dirs, run_id=run_id)

    metrics = {
        "run_id": run_id,
        "competition": competition,
        "model": "blend",
        "metric": data_cfg["metric"],
        "cv_score": best["cv_score"],
        "source_run_ids": run_ids,
        "blend_method": best["method"],
        "weights": best["weights"],
        "candidate_scores": [
            {"method": item["method"], "weights": item["weights"], "cv_score": item["cv_score"]}
            for item in scored
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    _log_blend(metrics, cfg)
    print(f"[blend] best={best['method']} score={best['cv_score']:.6f} -> {run_dir}")
    return run_dir


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _assert_compatible_manifests(run_dirs: list[Path]) -> None:
    manifests = [_read_json(path / "fold_manifest.json") for path in run_dirs]
    first = _manifest_key(manifests[0])
    for run_dir, manifest in zip(run_dirs[1:], manifests[1:]):
        current = _manifest_key(manifest)
        if current != first:
            raise ValueError(f"fold_manifest mismatch: {run_dirs[0]} vs {run_dir}")


def _manifest_key(manifest: dict[str, Any]) -> tuple[Any, ...]:
    folds = manifest.get("folds") or []
    return (
        manifest.get("competition"),
        manifest.get("objective"),
        tuple(manifest.get("seeds") or []),
        tuple((item.get("seed"), item.get("fold"), item.get("valid_index_sha256")) for item in folds),
    )


def _read_prediction_frame(path: Path, *, required_target: bool) -> dict[str, Any]:
    df = pd.read_parquet(path)
    pred_cols = [col for col in df.columns if str(col).startswith("pred_")]
    if pred_cols:
        pred = df[pred_cols].to_numpy()
    else:
        pred = df["prediction"].to_numpy()
    out: dict[str, Any] = {"pred": pred}
    if required_target:
        out["target"] = df["target"]
        out["trained"] = df.get("trained", pd.Series([True] * len(df), index=df.index))
    return out


def _blend_candidates(oof_preds: list[np.ndarray], test_preds: list[np.ndarray]) -> list[dict[str, Any]]:
    candidates = [_candidate("mean", _uniform(len(oof_preds)), oof_preds, test_preds)]
    candidates.append({
        "method": "rank_average",
        "weights": _uniform(len(oof_preds)),
        "oof": _rank_average(oof_preds),
        "test": _rank_average(test_preds),
    })
    if len(oof_preds) == 2:
        for weight in np.linspace(0.0, 1.0, 11):
            candidates.append(_candidate("weight_grid", [float(weight), float(1.0 - weight)], oof_preds, test_preds))
    return candidates


def _candidate(method: str, weights: list[float], oof_preds: list[np.ndarray], test_preds: list[np.ndarray]) -> dict[str, Any]:
    return {
        "method": method,
        "weights": weights,
        "oof": _weighted_average(oof_preds, weights),
        "test": _weighted_average(test_preds, weights),
    }


def _weighted_average(preds: list[np.ndarray], weights: list[float]) -> np.ndarray:
    stacked = np.stack(preds, axis=0)
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    return np.tensordot(w, stacked, axes=(0, 0))


def _rank_average(preds: list[np.ndarray]) -> np.ndarray:
    ranked = [_rank_array(pred) for pred in preds]
    avg = np.mean(ranked, axis=0)
    if avg.ndim == 2:
        row_sum = avg.sum(axis=1, keepdims=True)
        row_sum[row_sum == 0] = 1.0
        return avg / row_sum
    return avg


def _rank_array(pred: np.ndarray) -> np.ndarray:
    if pred.ndim == 1:
        return pd.Series(pred).rank(pct=True).to_numpy()
    cols = [pd.Series(pred[:, i]).rank(pct=True).to_numpy() for i in range(pred.shape[1])]
    return np.column_stack(cols)


def _uniform(n: int) -> list[float]:
    return [1.0 / n] * n


def _choose_best(candidates: list[dict[str, Any]], *, metric: str) -> dict[str, Any]:
    reverse = metric_is_higher_better(metric)
    return sorted(candidates, key=lambda item: item["cv_score"], reverse=reverse)[0]


def _write_prediction_frame(path: Path, pred: np.ndarray, *, target: np.ndarray | None = None, trained: np.ndarray | None = None) -> None:
    if pred.ndim == 1:
        df = pd.DataFrame({"row_id": range(len(pred)), "prediction": pred})
    else:
        df = pd.DataFrame(pred, columns=[f"pred_{i}" for i in range(pred.shape[1])])
        df.insert(0, "row_id", range(len(pred)))
    if target is not None:
        df.insert(1, "target", target)
    if trained is not None:
        df["trained"] = trained
    df.to_parquet(path, index=False)


def _write_submission(path: Path, pred: np.ndarray, *, cfg: dict[str, Any], source_dir: Path) -> None:
    data_cfg = cfg.get("data", cfg)
    source_sub = pd.read_csv(source_dir / "submission.csv")
    target_col = data_cfg.get("submission_target") or data_cfg.get("target", "target")
    id_col = data_cfg.get("id_col")
    if data_cfg.get("objective") == "multiclass" and pred.ndim > 1:
        labels = _read_label_classes(source_dir)
        values = [labels[i] for i in np.argmax(pred, axis=1)] if labels else np.argmax(pred, axis=1)
    else:
        values = pred
    out: dict[str, Any] = {}
    if id_col and id_col in source_sub.columns:
        out[id_col] = source_sub[id_col].to_numpy()
    out[target_col] = values
    pd.DataFrame(out).to_csv(path, index=False)


def _read_label_classes(source_dir: Path) -> list[str] | None:
    path = source_dir / "model" / "preprocess.json"
    if not path.exists():
        return None
    payload = _read_json(path)
    return payload.get("label_classes")


def _write_blend_manifest(path: Path, *, source_dirs: list[Path], run_id: str) -> None:
    base = _read_json(source_dirs[0] / "fold_manifest.json")
    base["run_id"] = run_id
    base["blend_source_run_ids"] = [item.name for item in source_dirs]
    base["created_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(base, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _log_blend(metrics: dict[str, Any], cfg: dict[str, Any]) -> None:
    try:
        from utils import bq

        project, dataset = bq.load_gcp()
        if not project:
            print(f"[blend] gcpProject 未設定: BQ 記録を skip run_id={metrics['run_id']}")
            return
        table = f"{dataset}.experiments"
        bq.execute(project, f"""
            CREATE TABLE IF NOT EXISTS {table} (
                run_id STRING,
                recorded_at TIMESTAMP,
                cv_score FLOAT64,
                metric STRING,
                competition STRING,
                params STRING,
                notes STRING,
                source STRING
            )
        """)
        bq.insert_row(project, table, ["run_id", "recorded_at", "cv_score", "metric", "competition", "params", "notes", "source"], {
            "run_id": metrics["run_id"],
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "cv_score": metrics["cv_score"],
            "metric": metrics["metric"],
            "competition": metrics["competition"],
            "params": json.dumps({
                "source_run_ids": metrics["source_run_ids"],
                "blend_method": metrics["blend_method"],
                "weights": metrics["weights"],
            }, ensure_ascii=False),
            "notes": "OOF blend via runner.ops.blend",
            "source": "blend",
        })
        print(f"[blend] BQ {table} <- run_id={metrics['run_id']}")
    except Exception as exc:  # noqa: BLE001 - blend artifact is still valid without BQ logging.
        print(f"[blend] WARN: BQ 記録失敗: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
