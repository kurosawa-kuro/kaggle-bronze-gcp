"""ROGII wellbore geology prediction directory loader."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


HORIZONTAL_SUFFIX = "__horizontal_well.csv"


def load_data(
    raw_dir: Path,
    *,
    train_row_limit: int | None = None,
    test_row_limit: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = _load_train(raw_dir / "train")
    test_df = _load_test(raw_dir / "test", raw_dir / "sample_submission.csv")
    if train_row_limit is not None and len(train_df) > train_row_limit:
        train_df = train_df.sample(n=train_row_limit, random_state=42).sort_values(["well_id", "row_index"])
    if test_row_limit is not None:
        test_df = test_df.head(test_row_limit)
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def _load_train(train_dir: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(train_dir.glob(f"*{HORIZONTAL_SUFFIX}")):
        well_id = _well_id(path)
        df = pd.read_csv(path)
        df = _add_identity(df, well_id)
        if "TVT_input" not in df.columns or "TVT" not in df.columns:
            raise ValueError(f"ROGII train horizontal file lacks TVT/TVT_input: {path}")
        target_zone = df["TVT_input"].isna()
        frames.append(_feature_columns(df.loc[target_zone], train=True))
    if not frames:
        raise FileNotFoundError(f"no ROGII train horizontal files found in {train_dir}")
    return pd.concat(frames, ignore_index=True)


def _load_test(test_dir: Path, sample_path: Path) -> pd.DataFrame:
    if not sample_path.exists():
        raise FileNotFoundError(sample_path)
    sample = pd.read_csv(sample_path)
    if "id" not in sample.columns:
        raise ValueError(f"sample_submission.csv must contain id column: {sample_path}")
    by_well: dict[str, list[int]] = {}
    for sub_id in sample["id"].astype(str):
        well_id, row_index = _parse_submission_id(sub_id)
        by_well.setdefault(well_id, []).append(row_index)

    frames = []
    for well_id, row_indexes in by_well.items():
        path = test_dir / f"{well_id}{HORIZONTAL_SUFFIX}"
        if not path.exists():
            raise FileNotFoundError(f"sample_submission references missing test well: {path}")
        df = _add_identity(pd.read_csv(path), well_id)
        selected = df.set_index("row_index").loc[row_indexes].reset_index()
        frames.append(_feature_columns(selected, train=False))
    out = pd.concat(frames, ignore_index=True)
    order = {sub_id: i for i, sub_id in enumerate(sample["id"].astype(str))}
    out["_sample_order"] = out["id"].map(order)
    return out.sort_values("_sample_order").drop(columns=["_sample_order"]).reset_index(drop=True)


def _add_identity(df: pd.DataFrame, well_id: str) -> pd.DataFrame:
    out = df.copy()
    out.insert(0, "row_index", out.index.astype(int))
    out.insert(0, "well_id", well_id)
    out.insert(0, "id", [f"{well_id}_{idx}" for idx in out["row_index"]])
    return out


def _feature_columns(df: pd.DataFrame, *, train: bool) -> pd.DataFrame:
    cols = ["id", "well_id", "row_index", "MD", "X", "Y", "Z", "GR", "TVT_input"]
    if train:
        cols.append("TVT")
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"ROGII required columns missing: {missing}")
    return df[cols].copy()


def _well_id(path: Path) -> str:
    name = path.name
    if not name.endswith(HORIZONTAL_SUFFIX):
        raise ValueError(f"not a ROGII horizontal well file: {path}")
    return name[: -len(HORIZONTAL_SUFFIX)]


def _parse_submission_id(submission_id: str) -> tuple[str, int]:
    well_id, sep, row = submission_id.rpartition("_")
    if not sep or not well_id:
        raise ValueError(f"invalid ROGII submission id: {submission_id}")
    return well_id, int(row)
