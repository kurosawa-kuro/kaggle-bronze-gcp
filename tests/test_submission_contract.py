import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines.score import build_submission_frame, write_submission_from_predictions
from runner.ops.compare import _sql


class SubmissionContractTest(unittest.TestCase):
    def test_sample_submission_controls_columns_and_order(self):
        sample = pd.DataFrame({"id": [30, 10, 20], "target": [0.0, 0.0, 0.0]})
        test_df = pd.DataFrame({"id": [30, 10, 20], "feature": [1.0, 2.0, 3.0]})
        sub, contract = build_submission_frame(
            np.array([0.3, 0.1, 0.2]),
            cfg={"data": {"id_col": "id", "target": "target", "objective": "regression"}},
            original_test=test_df,
            sample=sample,
        )

        self.assertEqual(sub.columns.tolist(), ["id", "target"])
        self.assertEqual(sub["id"].tolist(), [30, 10, 20])
        self.assertEqual(sub["target"].tolist(), [0.3, 0.1, 0.2])
        self.assertFalse(contract["fallback"])
        self.assertEqual(contract["target_columns"], ["target"])

    def test_rogii_like_sample_order_is_preserved_and_contract_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw"
            raw.mkdir()
            pd.DataFrame({"id": ["well_2", "well_1"], "tvt": [0.0, 0.0]}).to_csv(
                raw / "sample_submission.csv", index=False
            )
            out = root / "submission.csv"
            write_submission_from_predictions(
                out,
                np.array([12.5, 11.5]),
                cfg={
                    "data": {
                        "comp": "rogii-wellbore-geology-prediction",
                        "id_col": "id",
                        "target": "TVT",
                        "submission_target": "tvt",
                        "objective": "regression",
                        "raw_dir": str(raw),
                    }
                },
                original_test=pd.DataFrame({"id": ["well_2", "well_1"]}),
            )

            sub = pd.read_csv(out)
            contract = json.loads((root / "submission_contract.json").read_text(encoding="utf-8"))

        self.assertEqual(sub.columns.tolist(), ["id", "tvt"])
        self.assertEqual(sub["id"].tolist(), ["well_2", "well_1"])
        self.assertEqual(sub["tvt"].tolist(), [12.5, 11.5])
        self.assertFalse(contract["fallback"])
        self.assertEqual(contract["columns"], ["id", "tvt"])
        self.assertEqual(contract["row_count"], 2)
        self.assertIsNotNone(contract["sample_sha256"])

    def test_compare_sql_joins_by_competition_and_run_id(self):
        sql = _sql(
            "dataset",
            competition=None,
            source=None,
            run_like=None,
            limit=10,
            direction=None,
        )
        self.assertIn("ON e.run_id = c.run_id AND e.competition = c.competition", sql)
        self.assertIn("ON e.run_id = s.run_id AND e.competition = s.competition", sql)
        self.assertIn("PARTITION BY\n                      competition,", sql)


if __name__ == "__main__":
    unittest.main()
