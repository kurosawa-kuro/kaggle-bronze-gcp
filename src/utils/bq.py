"""BigQuery 共通ユーティリティ（google-cloud-bigquery Python client 経由）。

tabular メタデータの正本を BigQuery に統一する方針（ADR 0002）に伴い、
costs.py / logger.py / compare.py が共有する最小ヘルパ。
Vertex コンテナ内でも動くよう、`bq` CLI ではなく ADC / attached Service Account
で認証する Python client を使う。
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from google.cloud import bigquery


def clean_env() -> dict:
    """外部 CLI 互換用。gcloud 等へ PYTHONPATH=src を渡さないために残す。"""
    return {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}


def load_gcp(path: str | Path = "env/project.yaml") -> tuple[str | None, str]:
    """(gcpProject, bqDataset) を返す。project 未設定なら (None, dataset)。"""
    p = Path(path)
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    cfg = cfg or {}
    gcp = cfg.get("gcp", {})
    project = cfg.get("gcpProject") or gcp.get("project")
    dataset = cfg.get("bqDataset", "kaggle_ops")
    return project, dataset


def client(project: str) -> bigquery.Client:
    return bigquery.Client(project=project)


def query(project: str, sql: str, fmt: str | None = None) -> str:
    rows = list(client(project).query(sql).result())
    if fmt == "json":
        return json.dumps([_row_to_jsonable(dict(row)) for row in rows], ensure_ascii=False)
    if fmt == "pretty":
        return _pretty(rows)
    return "\n".join(str(tuple(row.values())) for row in rows) + ("\n" if rows else "")


def execute(project: str, sql: str) -> None:
    client(project).query(sql).result()


def insert_row(
    project: str,
    table: str,
    columns: list[str],
    row: dict,
    ts_cols: set[str] | None = None,
) -> None:
    del ts_cols  # Python client accepts ISO timestamp strings for TIMESTAMP columns.
    payload = {column: row.get(column) for column in columns}
    errors = client(project).insert_rows_json(_table_ref(project, table), [payload])
    if errors:
        raise RuntimeError(f"[bq] insert_rows_json failed: {errors}")


def _table_ref(project: str, table: str) -> str:
    parts = table.split(".")
    if len(parts) == 2:
        return f"{project}.{table}"
    return table


def _row_to_jsonable(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (datetime, date)):
            out[key] = value.isoformat()
        elif isinstance(value, Decimal):
            out[key] = float(value)
        else:
            out[key] = value
    return out


def _pretty(rows: list[bigquery.table.Row]) -> str:
    if not rows:
        return "(no rows)\n"
    dicts = [_row_to_jsonable(dict(row)) for row in rows]
    columns = list(dicts[0].keys())
    widths = {
        col: max(len(col), *(len(str(row.get(col, ""))) for row in dicts))
        for col in columns
    }
    sep = "+-" + "-+-".join("-" * widths[col] for col in columns) + "-+"
    header = "| " + " | ".join(col.ljust(widths[col]) for col in columns) + " |"
    body = [
        "| " + " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns) + " |"
        for row in dicts
    ]
    return "\n".join([sep, header, sep, *body, sep]) + "\n"
