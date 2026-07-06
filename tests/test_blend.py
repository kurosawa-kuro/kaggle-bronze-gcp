import json
import tempfile
import unittest
from pathlib import Path

from runner.ops.blend import _assert_compatible_manifests, _choose_best


class BlendTest(unittest.TestCase):
    def test_manifest_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            left.mkdir()
            right.mkdir()
            base = {
                "competition": "comp",
                "objective": "multiclass",
                "strategy": "stratified",
                "group_col": None,
                "seeds": [42],
                "folds": [{"seed": 42, "fold": 0, "valid_index_sha256": "aaa"}],
            }
            (left / "fold_manifest.json").write_text(json.dumps(base), encoding="utf-8")
            changed = {**base, "folds": [{"seed": 42, "fold": 0, "valid_index_sha256": "bbb"}]}
            (right / "fold_manifest.json").write_text(json.dumps(changed), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "fold_manifest mismatch"):
                _assert_compatible_manifests([left, right])

    def test_choose_best_metric_direction(self):
        candidates = [
            {"cv_score": 0.4, "method": "a"},
            {"cv_score": 0.3, "method": "b"},
        ]
        self.assertEqual(_choose_best(candidates, metric="logloss")["method"], "b")
        self.assertEqual(_choose_best(candidates, metric="auc")["method"], "a")

    def test_manifest_legacy_metadata_is_compatible_when_hashes_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            left.mkdir()
            right.mkdir()
            base = {
                "competition": "comp",
                "objective": "multiclass",
                "seeds": [42],
                "folds": [{"seed": 42, "fold": 0, "valid_index_sha256": "aaa"}],
            }
            (left / "fold_manifest.json").write_text(json.dumps(base), encoding="utf-8")
            enriched = {**base, "strategy": "stratified", "group_col": None}
            (right / "fold_manifest.json").write_text(json.dumps(enriched), encoding="utf-8")

            _assert_compatible_manifests([left, right])


if __name__ == "__main__":
    unittest.main()
