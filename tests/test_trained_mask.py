import unittest

import numpy as np
import pandas as pd

from pipelines.splits import make_splits
from runner.experiment.train import _trained_mask_from_splits


class TrainedMaskTest(unittest.TestCase):
    def test_max_folds_marks_only_trained_validation_fold(self):
        X = pd.DataFrame({"x": range(20)})
        y = pd.Series([0, 1] * 10)
        expected = _mask_from_expected_splits(
            X,
            y,
            objective="binary",
            cv_strategy=None,
            n_folds=5,
            seed=42,
            max_folds=1,
            groups=None,
        )

        mask = _trained_mask_from_splits(
            X,
            y,
            objective="binary",
            cv_strategy=None,
            n_folds=5,
            seed=42,
            max_folds=1,
            groups=None,
        )

        self.assertEqual(mask.dtype, np.bool_)
        self.assertEqual(mask.tolist(), expected.tolist())
        self.assertEqual(int(mask.sum()), 4)
        self.assertLess(int(mask.sum()), len(y))

    def test_all_folds_marks_every_row(self):
        X = pd.DataFrame({"x": range(20)})
        y = pd.Series([0, 1] * 10)

        mask = _trained_mask_from_splits(
            X,
            y,
            objective="binary",
            cv_strategy=None,
            n_folds=5,
            seed=42,
            max_folds=None,
            groups=None,
        )

        self.assertTrue(mask.all())

    def test_zero_oof_predictions_are_not_treated_as_untrained(self):
        X = pd.DataFrame({"x": range(20)})
        y = pd.Series(np.linspace(-1.0, 1.0, 20))
        oof = np.zeros(len(y))

        split_mask = _trained_mask_from_splits(
            X,
            y,
            objective="regression",
            cv_strategy=None,
            n_folds=5,
            seed=42,
            max_folds=1,
            groups=None,
        )
        old_value_based_mask = oof != 0

        self.assertGreater(int(split_mask.sum()), 0)
        self.assertFalse(old_value_based_mask.any())
        self.assertFalse(np.array_equal(split_mask, old_value_based_mask))

    def test_group_strategy_marks_only_trained_validation_groups(self):
        X = pd.DataFrame({"x": range(12)})
        y = pd.Series(np.linspace(0.0, 1.0, 12))
        groups = pd.Series(["a", "a", "b", "b", "c", "c", "d", "d", "e", "e", "f", "f"])
        expected = _mask_from_expected_splits(
            X,
            y,
            objective="regression",
            cv_strategy="group",
            n_folds=3,
            seed=42,
            max_folds=1,
            groups=groups,
        )

        mask = _trained_mask_from_splits(
            X,
            y,
            objective="regression",
            cv_strategy="group",
            n_folds=3,
            seed=42,
            max_folds=1,
            groups=groups,
        )

        self.assertEqual(mask.tolist(), expected.tolist())
        self.assertEqual(int(mask.sum()), 4)
        self.assertEqual(set(groups[mask]), set(groups.iloc[np.flatnonzero(expected)]))


def _mask_from_expected_splits(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    objective: str,
    cv_strategy: str | None,
    n_folds: int,
    seed: int,
    max_folds: int | None,
    groups: pd.Series | None,
) -> np.ndarray:
    splits = make_splits(
        X,
        y,
        objective=objective,
        strategy=cv_strategy,
        n_folds=n_folds,
        seed=seed,
        groups=groups,
    )
    if max_folds is not None:
        splits = splits[:max_folds]
    mask = np.zeros(len(y), dtype=bool)
    for _, valid_idx in splits:
        mask[valid_idx] = True
    return mask


if __name__ == "__main__":
    unittest.main()
