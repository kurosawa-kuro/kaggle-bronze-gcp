"""Compare experiment runs from BigQuery."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from utils import bq


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare BigQuery experiment runs")
    parser.add_argument("--project-config", default="env/project.yaml")
    parser.add_argument("--competition", "--comp", dest="competition", default=None)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--source", default=None)
    parser.add_argument("--run-like", default=None, help="SQL LIKE pattern for run_id")
    parser.add_argument("--higher-is-better", action="store_true", help="Sort cv_score descending")
    parser.add_argument("--lower-is-better", action="store_true", help="Sort cv_score ascending")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    project, dataset = bq.load_gcp(args.project_config)
    if not project:
        raise SystemExit("[compare] gcpProject が env/project.yaml に無い")
    pcfg = _load_yaml(Path(args.project_config))
    competition = args.competition or pcfg.get("competition")
    direction = _sort_direction(higher=args.higher_is_better, lower=args.lower_is_better)
    print(bq.query(project, _sql(dataset, competition=competition, source=args.source,
                                 run_like=args.run_like, limit=args.limit,
                                 direction=direction), fmt="pretty"))
    return 0


def _sql(
    dataset: str,
    *,
    competition: str | None,
    source: str | None,
    run_like: str | None,
    limit: int,
    direction: str | None,
) -> str:
    filters = []
    if competition:
        filters.append(f"e.competition = '{_escape(competition)}'")
    if source:
        filters.append(f"e.source = '{_escape(source)}'")
    if run_like:
        filters.append(f"e.run_id LIKE '{_escape(run_like)}'")
    where = "WHERE " + " AND ".join(filters) if filters else ""
    score_key = (
        "CASE "
        "WHEN LOWER(e.metric) IN ('auc', 'accuracy', 'map', 'ndcg', 'f1') THEN -e.cv_score "
        "ELSE e.cv_score END"
    )
    if direction == "desc":
        score_key = "-e.cv_score"
    elif direction == "asc":
        score_key = "e.cv_score"
    return f"""
        SELECT
          e.run_id,
          e.recorded_at,
          e.cv_score,
          e.metric,
          e.competition,
          e.source,
          ROUND(SUM(c.est_jpy), 1) AS est_jpy,
          COUNT(c.resource_id) AS cost_rows
        FROM `{dataset}.experiments` e
        LEFT JOIN `{dataset}.cost_estimates` c
          ON e.run_id = c.run_id
        {where}
        GROUP BY e.run_id, e.recorded_at, e.cv_score, e.metric, e.competition, e.source
        ORDER BY {score_key} ASC, e.recorded_at DESC
        LIMIT {int(limit)}
    """


def _sort_direction(*, higher: bool, lower: bool) -> str | None:
    if higher and lower:
        raise SystemExit("[compare] --higher-is-better と --lower-is-better は同時指定できません")
    if higher:
        return "desc"
    if lower:
        return "asc"
    return None


def _escape(value: str) -> str:
    return value.replace("'", "''")


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


if __name__ == "__main__":
    raise SystemExit(main())
