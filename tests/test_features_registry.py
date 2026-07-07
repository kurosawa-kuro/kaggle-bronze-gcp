import unittest

import pandas as pd

from features import apply_feature_registry


class FeatureRegistryTest(unittest.TestCase):
    def test_base_features_keep_columns(self):
        train = pd.DataFrame({"a": [1, 2]})
        test = pd.DataFrame({"a": [3]})

        out_train, out_test = apply_feature_registry(train, test, ["base"])

        self.assertEqual(out_train.columns.tolist(), ["a"])
        self.assertEqual(out_test.columns.tolist(), ["a"])

    def test_unknown_feature_set_raises(self):
        with self.assertRaisesRegex(ValueError, "unknown feature set"):
            apply_feature_registry(pd.DataFrame({"a": [1]}), pd.DataFrame({"a": [2]}), ["missing"])


if __name__ == "__main__":
    unittest.main()
