import unittest

import pandas as pd

from pipelines.splits import group_overlap_report, make_splits


class SplitTests(unittest.TestCase):
    def test_group_split_has_no_validation_group_overlap(self):
        X = pd.DataFrame({"x": range(8)})
        y = pd.Series([0, 1, 0, 1, 0, 1, 0, 1])
        groups = pd.Series(["a", "a", "b", "b", "c", "c", "d", "d"])

        splits = make_splits(
            X,
            y,
            objective="binary",
            strategy="group",
            n_folds=2,
            seed=42,
            groups=groups,
        )

        self.assertEqual(group_overlap_report(splits, groups)["overlap_count"], 0)

    def test_group_overlap_report_detects_bad_splits(self):
        groups = pd.Series(["a", "a", "b", "b"])
        bad_splits = [
            ([2, 3], [0, 1]),
            ([0, 3], [1, 2]),
        ]

        report = group_overlap_report(bad_splits, groups)

        self.assertGreater(report["overlap_count"], 0)


if __name__ == "__main__":
    unittest.main()
