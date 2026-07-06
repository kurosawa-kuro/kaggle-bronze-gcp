"""BigQuery ledger for Kaggle submissions."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

from utils import bq

TABLE_NAME = "submissions"
COLUMNS = [
    "submission_ref",
    "run_id",
    "competition",
    "submitted_at",
    "message",
    "cv_score",
    "public_lb",
    "private_lb",
    "status",
    "selected_final",
    "notes",
    "source",
    "recorded_at",
    "updated_at",
]
TS_COLS = {"submitted_at", "recorded_at", "updated_at"}
FLOAT_COLS = {"cv_score", "public_lb", "private_lb"}
BOOL_COLS = {"selected_final"}
RUN_ID_RE = re.compile(r"\[run_id=([^\]]+)\]")
_ensured = False


def table(dataset: str) -> str:
    return f"{dataset}.{TABLE_NAME}"


def ensure(project: str, dataset: str) -> None:
    global _ensured
    if _ensured:
        return
    bq.execute(project, f"""
        CREATE TABLE IF NOT EXISTS {table(dataset)} (
            submission_ref STRING,
            run_id          STRING,
            competition     STRING,
            submitted_at    TIMESTAMP,
            message         STRING,
            cv_score        FLOAT64,
            public_lb       FLOAT64,
            private_lb      FLOAT64,
            status          STRING,
            selected_final  BOOL,
            notes           STRING,
            source          STRING,
            recorded_at     TIMESTAMP,
            updated_at      TIMESTAMP
        )
    """)
    _ensured = True


def message_with_run_id(message: str, run_id: str) -> str:
    if f"[run_id={run_id}]" in message:
        return message
    return f"{message} [run_id={run_id}]"


def extract_run_id(message: str) -> str | None:
    match = RUN_ID_RE.search(message or "")
    return match.group(1) if match else None


def record_submit_attempt(
    *,
    project: str,
    dataset: str,
    competition: str,
    run_id: str,
    message: str,
    run_dir: Path,
    status: str,
    notes: str = "",
) -> None:
    ensure(project, dataset)
    metrics = _load_metrics(run_dir)
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "submission_ref": None,
        "run_id": run_id,
        "competition": competition,
        "submitted_at": now,
        "message": message,
        "cv_score": metrics.get("cv_score"),
        "public_lb": None,
        "private_lb": None,
        "status": status,
        "selected_final": False,
        "notes": notes,
        "source": "submit.py",
        "recorded_at": now,
        "updated_at": now,
    }
    bq.insert_row(project, table(dataset), COLUMNS, row, TS_COLS)


def sync_from_kaggle(*, project: str, dataset: str, competition: str, page_size: int = 200) -> int:
    ensure(project, dataset)
    rows = kaggle_submissions(competition=competition, page_size=page_size)
    count = 0
    for row in rows:
        try:
            merge_submission(project=project, dataset=dataset, row=row)
        except Exception as exc:  # noqa: BLE001 - streaming buffer 中は append で同期を進める
            if "streaming buffer" not in str(exc):
                raise
            insert_submission(project=project, dataset=dataset, row=row)
        count += 1
    return count


def kaggle_submissions(*, competition: str, page_size: int = 200) -> list[dict[str, Any]]:
    cmd = [
        sys.executable,
        "-m",
        "kaggle",
        "competitions",
        "submissions",
        "-c",
        competition,
        "--csv",
        "--page-size",
        str(page_size),
    ]
    result = subprocess.run(
        cmd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=bq.clean_env(),
    )
    return parse_submissions_csv(result.stdout, competition=competition)


def parse_submissions_csv(text: str, *, competition: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(StringIO(text))
    required = {"ref", "date", "description", "status", "publicScore", "privateScore"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise ValueError(f"unexpected kaggle submissions CSV header: {reader.fieldnames}")
    now = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for raw in reader:
        message = raw.get("description") or ""
        rows.append({
            "submission_ref": raw.get("ref") or None,
            "run_id": extract_run_id(message),
            "competition": competition,
            "submitted_at": _parse_kaggle_ts(raw.get("date") or ""),
            "message": message,
            "cv_score": None,
            "public_lb": _score(raw.get("publicScore")),
            "private_lb": _score(raw.get("privateScore")),
            "status": raw.get("status") or None,
            "selected_final": False,
            "notes": "synced from kaggle submissions",
            "source": "lb-sync",
            "recorded_at": now,
            "updated_at": now,
        })
    return rows


def merge_submission(*, project: str, dataset: str, row: dict[str, Any]) -> None:
    ensure(project, dataset)
    row = {column: row.get(column) for column in COLUMNS}
    if row.get("updated_at") is None:
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
    if row.get("recorded_at") is None:
        row["recorded_at"] = row["updated_at"]
    select = ",\n              ".join(f"{_literal(column, row[column])} AS {column}" for column in COLUMNS)
    update = ",\n              ".join(
        f"{column} = COALESCE(S.{column}, T.{column})"
        for column in COLUMNS
        if column not in {"competition", "run_id", "message", "recorded_at"}
    )
    insert_cols = ", ".join(COLUMNS)
    insert_values = ", ".join(f"S.{column}" for column in COLUMNS)
    bq.execute(project, f"""
        MERGE `{project}.{dataset}.{TABLE_NAME}` T
        USING (
            SELECT {select}
        ) S
        ON T.competition = S.competition
           AND (
               (S.submission_ref IS NOT NULL AND T.submission_ref = S.submission_ref)
               OR (S.run_id IS NOT NULL AND T.run_id = S.run_id AND T.message = S.message)
               OR (
                   T.submission_ref IS NULL
                   AND T.run_id IS NULL
                   AND T.submitted_at = S.submitted_at
                   AND T.message = S.message
               )
           )
        WHEN MATCHED THEN UPDATE SET
              {update}
        WHEN NOT MATCHED THEN INSERT ({insert_cols})
        VALUES ({insert_values})
    """)


def insert_submission(*, project: str, dataset: str, row: dict[str, Any]) -> None:
    ensure(project, dataset)
    row = {column: row.get(column) for column in COLUMNS}
    if row.get("updated_at") is None:
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
    if row.get("recorded_at") is None:
        row["recorded_at"] = row["updated_at"]
    bq.insert_row(project, table(dataset), COLUMNS, row, TS_COLS)


def _load_metrics(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "metrics.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _score(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_kaggle_ts(value: str) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat()
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    return dt.replace(tzinfo=timezone.utc).isoformat()


def _literal(column: str, value: Any) -> str:
    if value is None:
        if column in TS_COLS:
            return "CAST(NULL AS TIMESTAMP)"
        if column in FLOAT_COLS:
            return "CAST(NULL AS FLOAT64)"
        if column in BOOL_COLS:
            return "CAST(NULL AS BOOL)"
        return "CAST(NULL AS STRING)"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("'", "''")
    if column in TS_COLS:
        return f"TIMESTAMP('{text}')"
    return f"'{text}'"
