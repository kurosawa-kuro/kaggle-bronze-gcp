import tempfile
import unittest
from pathlib import Path

import pandas as pd

from competitions.rogii import load_data


class RogiiLoaderTest(unittest.TestCase):
    def test_loads_target_zone_and_sample_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            (raw / "train").mkdir()
            (raw / "test").mkdir()
            _horizontal(
                raw / "train" / "abc12345__horizontal_well.csv",
                tvt=[10.0, 11.0, 12.0],
                tvt_input=[10.0, None, None],
            )
            _horizontal(
                raw / "test" / "abc12345__horizontal_well.csv",
                tvt=[0.0, 0.0, 0.0],
                tvt_input=[10.0, None, None],
                include_target=False,
            )
            pd.DataFrame({"id": ["abc12345_2", "abc12345_1"], "tvt": [0.0, 0.0]}).to_csv(
                raw / "sample_submission.csv", index=False
            )

            train_df, test_df = load_data(raw)

        self.assertEqual(train_df["id"].tolist(), ["abc12345_1", "abc12345_2"])
        self.assertEqual(train_df["TVT"].tolist(), [11.0, 12.0])
        self.assertEqual(train_df["well_id"].tolist(), ["abc12345", "abc12345"])
        self.assertEqual(test_df["id"].tolist(), ["abc12345_2", "abc12345_1"])
        self.assertNotIn("TVT", test_df.columns)


def _horizontal(path: Path, *, tvt: list[float], tvt_input: list[float | None], include_target: bool = True) -> None:
    df = pd.DataFrame({
        "MD": [100.0, 101.0, 102.0],
        "X": [1.0, 1.1, 1.2],
        "Y": [2.0, 2.1, 2.2],
        "Z": [3.0, 3.1, 3.2],
        "GR": [50.0, 51.0, 52.0],
        "TVT_input": tvt_input,
    })
    if include_target:
        df.insert(5, "TVT", tvt)
    df.to_csv(path, index=False)


if __name__ == "__main__":
    unittest.main()
