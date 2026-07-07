import unittest

import numpy as np

from pipelines.evaluate import (
    cv_score,
    higher_is_better_metric_names,
    metric_direction,
    metric_is_higher_better,
)
from runner.ops.compare import _sql


class MetricsTest(unittest.TestCase):
    def test_cv_score_supported_metrics(self):
        y_true = np.array([0, 1, 1, 0])
        y_pred = np.array([0.1, 0.8, 0.7, 0.2])

        self.assertAlmostEqual(cv_score(y_true, y_pred, metric="rmse"), 0.21213203435596428)
        self.assertAlmostEqual(cv_score(y_true, y_pred, metric="auc"), 1.0)
        self.assertLess(cv_score(y_true, y_pred, metric="logloss"), 0.25)

    def test_metric_direction_registry(self):
        self.assertEqual(metric_direction("auc"), "maximize")
        self.assertEqual(metric_direction("logloss"), "minimize")
        self.assertTrue(metric_is_higher_better("qwk"))
        self.assertFalse(metric_is_higher_better("rmse"))

    def test_direction_only_metric_requires_scorer_before_cv_use(self):
        with self.assertRaisesRegex(ValueError, "scorer 未実装"):
            cv_score(np.array([1, 0]), np.array([1, 0]), metric="accuracy")

    def test_compare_default_sort_uses_metric_registry(self):
        sql = _sql(
            "dataset",
            competition=None,
            source=None,
            run_like=None,
            limit=10,
            direction=None,
        )
        for metric in higher_is_better_metric_names():
            self.assertIn(f"'{metric}'", sql)
        self.assertIn("THEN -e.cv_score", sql)


if __name__ == "__main__":
    unittest.main()
