"""Prepare Vertex Batch Prediction JSONL input from the configured test set."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and upload batch prediction instances JSONL")
    parser.add_argument("--config", default="configs/lgbm_baseline.yaml")
    parser.add_argument("--project-config", default="env/project.yaml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit for a lightweight prediction check")
    parser.add_argument("--output-root", default="outputs/batch_input")
    parser.add_argument("--gcs-uri", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    config_path = Path(args.config).resolve()
    cfg = _load_yaml(config_path)
    pcfg = _load_yaml(Path(args.project_config))
    data_cfg = cfg.get("data", cfg)
    competition = data_cfg["comp"]
    bucket = pcfg.get("gcsBucket")
    if not bucket and not args.gcs_uri:
        raise SystemExit("[batch-input] gcsBucket が env/project.yaml に無い")

    os.environ["KBC_CONFIG_PATH"] = str(config_path)
    from pipelines.featurize import make_features
    from pipelines.ingest import load_data
    from utils.artifact_store import GcsPrefix, upload_file

    train_df, test_df = load_data()
    _, _, x_test = make_features(train_df, test_df)
    if args.limit is not None:
        x_test = x_test.head(args.limit)

    local_dir = Path(args.output_root) / competition / args.run_id
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / "instances.jsonl"
    _write_jsonl(local_path, x_test.values.tolist())
    meta_path = local_dir / "instances_meta.json"
    meta_path.write_text(json.dumps({
        "competition": competition,
        "run_id": args.run_id,
        "rows": int(len(x_test)),
        "columns": list(map(str, x_test.columns)),
        "source_config": str(config_path),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    gcs_uri = args.gcs_uri or f"gs://{bucket}/batch_input/{competition}/{args.run_id}/instances.jsonl"
    upload_file(local_path, GcsPrefix.parse(gcs_uri))
    print(f"[batch-input] wrote {len(x_test)} instances -> {local_path}")
    print(f"[batch-input] uploaded -> {gcs_uri}")
    return 0


def _write_jsonl(path: Path, rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


if __name__ == "__main__":
    raise SystemExit(main())
