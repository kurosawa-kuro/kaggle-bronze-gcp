"""Submit train.py to Vertex AI Custom Job."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit a Vertex AI Custom Job")
    parser.add_argument("--config", default="configs/lgbm_baseline.yaml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-config", default="env/project.yaml")
    parser.add_argument("--project", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--image-uri", default=None)
    parser.add_argument("--input-uri", default=None, help="gs:// source for raw data (default: gs://<bucket>/data/<comp>/raw)")
    parser.add_argument("--machine-type", default=None)
    parser.add_argument("--service-account", default=None)
    parser.add_argument("--timeout-hours", type=float, default=8.0)
    parser.add_argument("--smoke", action="store_true", help="Pass --smoke to train.py (one quick fold)")
    parser.add_argument("--spot", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sync", action="store_true", help="Wait for the job to finish")
    parser.add_argument("--poll-seconds", type=int, default=30, help="Polling interval for guarded --sync")
    parser.add_argument("--max-log-silence-minutes", type=float, default=None,
                        help="Cancel/fail guarded --sync when worker logs stop for this many minutes")
    parser.add_argument("--cancel-on-silence", action="store_true",
                        help="Cancel the Vertex job when --max-log-silence-minutes is exceeded")
    return parser.parse_args(argv)


def submit_from_config(
    *,
    config_path: str,
    run_id: str,
    project_config: str = "env/project.yaml",
    project: str | None = None,
    region: str | None = None,
    bucket: str | None = None,
    image_uri: str | None = None,
    input_uri: str | None = None,
    machine_type: str | None = None,
    service_account: str | None = None,
    timeout_hours: float = 8.0,
    smoke: bool = False,
    spot: bool = False,
    sync: bool = False,
    poll_seconds: int = 30,
    max_log_silence_minutes: float | None = None,
    cancel_on_silence: bool = False,
    dry_run: bool = False,
) -> str | dict:
    """Build + submit one Custom Job. Non-blocking (.submit()) unless sync=True.
    Returns the job resource name (or the plan dict when dry_run)."""
    project_cfg = _load_yaml(Path(project_config))
    train_cfg = _load_yaml(Path(config_path))
    data_cfg = train_cfg.get("data", train_cfg)

    gcp_cfg = project_cfg.get("gcp", {})
    project = project or project_cfg.get("gcpProject") or gcp_cfg.get("project")
    region = region or project_cfg.get("gcpRegion") or gcp_cfg.get("region", "us-central1")
    bucket = bucket or project_cfg.get("gcsBucket")
    image_uri = image_uri or project_cfg.get("imageUri")
    machine_type = machine_type or project_cfg.get("vertexMachineType", "n1-standard-4")
    service_account = service_account or project_cfg.get("vertexServiceAccount")
    competition = data_cfg["comp"]
    if not image_uri and project:
        image_uri = _image_uri(project_cfg, project=project, region=region)

    missing = [name for name, value in {
        "project": project,
        "bucket": bucket,
        "image_uri": image_uri,
    }.items() if not value]
    if missing:
        raise SystemExit(f"[vertex] missing required settings: {', '.join(missing)}")

    output_uri = f"gs://{bucket}/runs/{competition}/{run_id}"
    input_uri = input_uri or f"gs://{bucket}/data/{competition}/raw"
    # config はイメージにベイクせず base64 で渡す（新 config でも再ビルド不要）
    import base64
    config_b64 = base64.b64encode(Path(config_path).read_bytes()).decode("ascii")
    container_args = [
        "--config-b64", config_b64,
        "--run-id", run_id,
        "--output-uri", output_uri,
        "--input-uri", input_uri,
    ]
    if smoke:
        container_args.append("--smoke")
    worker_pool_specs = [{
        "machine_spec": {"machine_type": machine_type},
        "replica_count": 1,
        "container_spec": {
            "image_uri": image_uri,
            "command": ["python", "-m", "runner.experiment.train"],
            "args": container_args,
        },
    }]
    labels = {
        "purpose": "kaggle-bronze",
        "comp": _label_value(competition),
        "run_id": _label_value(run_id),
    }
    plan = {
        "project": project,
        "region": region,
        "display_name": f"kaggle-{competition}-{run_id}",
        "worker_pool_specs": worker_pool_specs,
        "staging_bucket": f"gs://{bucket}",
        "service_account": service_account,
        "scheduling_strategy": "SPOT" if spot else None,
        "labels": labels,
        "sync": sync,
    }
    if dry_run:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return plan

    from google.cloud import aiplatform

    aiplatform.init(project=project, location=region, staging_bucket=f"gs://{bucket}")
    job = aiplatform.CustomJob(
        display_name=plan["display_name"],
        worker_pool_specs=worker_pool_specs,
        labels=labels,
    )
    kwargs = {"service_account": service_account, "timeout": int(timeout_hours * 3600)}
    if spot:
        kwargs["scheduling_strategy"] = "SPOT"
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if sync and max_log_silence_minutes is None:
        job.run(sync=True, **kwargs)
    elif sync:
        job.submit(**kwargs)
        _watch_job(
            project=project,
            region=region,
            resource_name=job.resource_name,
            poll_seconds=poll_seconds,
            max_log_silence_minutes=max_log_silence_minutes,
            cancel_on_silence=cancel_on_silence,
        )
    else:
        job.submit(**kwargs)  # 非ブロッキング: 作成して即返る（fan-out 可能）
    print(f"[vertex] submitted {job.resource_name}  -> {output_uri}")
    return job.resource_name


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    submit_from_config(
        config_path=args.config,
        run_id=args.run_id,
        project_config=args.project_config,
        project=args.project,
        region=args.region,
        bucket=args.bucket,
        image_uri=args.image_uri,
        input_uri=args.input_uri,
        machine_type=args.machine_type,
        service_account=args.service_account,
        timeout_hours=args.timeout_hours,
        smoke=args.smoke,
        spot=args.spot,
        sync=args.sync,
        poll_seconds=args.poll_seconds,
        max_log_silence_minutes=args.max_log_silence_minutes,
        cancel_on_silence=args.cancel_on_silence,
        dry_run=args.dry_run,
    )
    return 0


def _label_value(value: str) -> str:
    """GCP label values: lowercase letters, digits, '-', '_'; max 63 chars."""
    import re

    return re.sub(r"[^a-z0-9_-]", "-", value.lower())[:63]


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _image_uri(project_cfg: dict, *, project: str, region: str) -> str:
    repo = project_cfg.get("artifactRegistryRepo", "kaggle")
    image_name = project_cfg.get("imageName", "kaggle-bronze-gcp")
    image_tag = project_cfg.get("imageTag", "latest")
    return f"{region}-docker.pkg.dev/{project}/{repo}/{image_name}:{image_tag}"


def _watch_job(
    *,
    project: str,
    region: str,
    resource_name: str,
    poll_seconds: int,
    max_log_silence_minutes: float,
    cancel_on_silence: bool,
) -> None:
    """Poll a Vertex job and fail fast when worker logs go stale."""
    job_id = resource_name.rsplit("/", 1)[-1]
    silence_seconds = max_log_silence_minutes * 60
    print(
        f"[vertex] guarded sync job={resource_name} "
        f"max_log_silence={max_log_silence_minutes}m cancel={cancel_on_silence}"
    )
    while True:
        state, start_time = _describe_state(project=project, region=region, job_id=job_id)
        latest_log = _latest_worker_log_time(project=project, job_id=job_id)
        reference = latest_log or start_time or datetime.now(timezone.utc)
        silent_for = (datetime.now(timezone.utc) - reference).total_seconds()
        latest_text = latest_log.isoformat() if latest_log else "none"
        print(f"[vertex] state={state} latest_log={latest_text} silent_for={silent_for / 60:.1f}m")
        if state == "JOB_STATE_SUCCEEDED":
            return
        if state in {"JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}:
            raise RuntimeError(f"Vertex job ended with {state}: {resource_name}")
        if state == "JOB_STATE_RUNNING" and silent_for > silence_seconds:
            message = (
                f"Vertex job log silence exceeded {max_log_silence_minutes} minutes: "
                f"{resource_name}"
            )
            if cancel_on_silence:
                _cancel_job(project=project, region=region, job_id=job_id)
                message += " (cancel requested)"
            raise TimeoutError(message)
        time.sleep(max(5, poll_seconds))


def _describe_state(*, project: str, region: str, job_id: str) -> tuple[str, datetime | None]:
    payload = _gcloud_json([
        "ai", "custom-jobs", "describe", job_id,
        "--region", region,
        "--project", project,
        "--format=json",
    ])
    return payload.get("state", "JOB_STATE_UNSPECIFIED"), _parse_ts(payload.get("startTime") or payload.get("createTime"))


def _latest_worker_log_time(*, project: str, job_id: str) -> datetime | None:
    result = subprocess.run(
        [
            "gcloud", "logging", "read",
            f'labels."ml.googleapis.com/job_id"="{job_id}"',
            "--project", project,
            "--limit", "1",
            "--format=json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    rows = json.loads(result.stdout or "[]")
    if not rows:
        return None
    return _parse_ts(rows[0].get("timestamp"))


def _cancel_job(*, project: str, region: str, job_id: str) -> None:
    subprocess.run(
        [
            "gcloud", "ai", "custom-jobs", "cancel", job_id,
            "--region", region,
            "--project", project,
            "--quiet",
        ],
        check=True,
    )


def _gcloud_json(args: list[str]) -> dict:
    result = subprocess.run(["gcloud", *args], check=True, text=True, capture_output=True)
    return json.loads(result.stdout or "{}")


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


if __name__ == "__main__":
    raise SystemExit(main())
