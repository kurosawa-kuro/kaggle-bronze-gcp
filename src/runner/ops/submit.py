"""Submit a run artifact's submission.csv to Kaggle."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml

from runner.ops import submission_ledger
from utils import bq


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit outputs/runs/.../submission.csv")
    parser.add_argument("--config", default="configs/lgbm_baseline.yaml")
    parser.add_argument("--competition", "--comp", dest="competition", default=None)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--message", "--msg", dest="message", required=True)
    parser.add_argument("--output-root", default="outputs/runs")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    competition = args.competition or cfg.get("data", cfg).get("comp")
    if not competition:
        raise SystemExit("[submit] competition is required")
    submission = Path(args.output_root) / competition / args.run_id / "submission.csv"
    if not submission.exists():
        raise SystemExit(f"[submit] missing submission: {submission}")
    message = submission_ledger.message_with_run_id(args.message, args.run_id)
    cmd = [
        sys.executable,
        "-m",
        "kaggle",
        "competitions",
        "submit",
        "-c",
        competition,
        "-f",
        str(submission),
        "-m",
        message,
    ]
    print("[submit] " + " ".join(cmd))
    # kaggle CLI に PYTHONPATH=src を渡すと自前モジュールが shadow されるため除去
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    returncode = subprocess.run(cmd, check=False, env=env).returncode
    if returncode == 0:
        _record_submission(competition=competition, run_id=args.run_id, message=message,
                           run_dir=submission.parent, status="SUBMITTED")
    return returncode


def _record_submission(*, competition: str, run_id: str, message: str, run_dir: Path, status: str) -> None:
    project, dataset = bq.load_gcp()
    if not project:
        print(f"[submit] gcpProject 未設定: submissions ledger skip run_id={run_id}")
        return
    try:
        submission_ledger.record_submit_attempt(
            project=project,
            dataset=dataset,
            competition=competition,
            run_id=run_id,
            message=message,
            run_dir=run_dir,
            status=status,
        )
        print(f"[submit] BQ {dataset}.submissions <- run_id={run_id}")
    except Exception as exc:  # noqa: BLE001 - Kaggle提出成功をBQ失敗で取り消さない
        print(f"[submit] WARN: submissions ledger failed run_id={run_id}: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
