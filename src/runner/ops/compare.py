"""Compare experiment runs from BigQuery."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from pipelines.evaluate import higher_is_better_metric_names
from utils import bq
from runner.ops import submission_ledger


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
    submission_ledger.ensure(project, dataset)
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
    higher_metrics = ", ".join(f"'{_escape(name)}'" for name in higher_is_better_metric_names())
    score_key = f"CASE WHEN LOWER(e.metric) IN ({higher_metrics}) THEN -e.cv_score ELSE e.cv_score END"
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
          s.submission_count,
          s.latest_submitted_at,
          s.public_lb,
          s.private_lb,
          s.submission_status,
          ROUND(SUM(c.est_jpy), 1) AS est_jpy,
          COUNT(c.resource_id) AS cost_rows
        FROM `{dataset}.experiments` e
        LEFT JOIN `{dataset}.cost_estimates` c
          ON e.run_id = c.run_id AND e.competition = c.competition
        LEFT JOIN (
          SELECT
            run_id,
            competition,
            submission_count,
            latest.submitted_at AS latest_submitted_at,
            latest.public_lb AS public_lb,
            latest.private_lb AS private_lb,
            latest.status AS submission_status
          FROM (
            SELECT
              run_id,
              competition,
              COUNT(*) AS submission_count,
              ARRAY_AGG(STRUCT(
                submitted_at,
                public_lb,
                private_lb,
                status
              ) ORDER BY IF(public_lb IS NULL, 1, 0), submitted_at DESC LIMIT 1)[OFFSET(0)] AS latest
            FROM (
              SELECT * EXCEPT (rn)
              FROM (
                SELECT
                  *,
                  ROW_NUMBER() OVER (
                    PARTITION BY
                      competition,
                      COALESCE(
                        CONCAT(run_id, '|', message),
                        submission_ref,
                        CONCAT(IFNULL(message, ''), '|', CAST(submitted_at AS STRING))
                      )
                    ORDER BY IF(public_lb IS NULL, 1, 0), updated_at DESC
                  ) AS rn
                FROM `{dataset}.submissions`
                WHERE run_id IS NOT NULL
              )
              WHERE rn = 1
            )
            GROUP BY run_id, competition
          )
        ) s
          ON e.run_id = s.run_id AND e.competition = s.competition
        {where}
        GROUP BY
          e.run_id, e.recorded_at, e.cv_score, e.metric, e.competition, e.source,
          s.submission_count, s.latest_submitted_at, s.public_lb, s.private_lb, s.submission_status
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
