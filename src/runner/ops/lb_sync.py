"""Sync Kaggle submission scores into BigQuery."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from runner.ops import submission_ledger
from utils import bq


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Kaggle public/private LB scores to BigQuery")
    parser.add_argument("--config", default="configs/lgbm_baseline.yaml")
    parser.add_argument("--project-config", default="env/project.yaml")
    parser.add_argument("--competition", "--comp", dest="competition", default=None)
    parser.add_argument("--page-size", type=int, default=200)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    project, dataset = bq.load_gcp(args.project_config)
    if not project:
        raise SystemExit("[lb-sync] gcpProject が env/project.yaml に無い")
    cfg = _load_yaml(Path(args.config))
    competition = args.competition or cfg.get("comp") or cfg.get("data", {}).get("comp")
    if not competition:
        raise SystemExit("[lb-sync] competition is required")
    count = submission_ledger.sync_from_kaggle(
        project=project,
        dataset=dataset,
        competition=competition,
        page_size=args.page_size,
    )
    print(f"[lb-sync] synced {count} submissions -> {dataset}.submissions")
    return 0


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


if __name__ == "__main__":
    raise SystemExit(main())
