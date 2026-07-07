import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipelines import ingest


class IngestCacheTest(unittest.TestCase):
    def test_interim_metadata_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            interim = Path(tmp)
            (interim / "_metadata.json").write_text(
                json.dumps({
                    "version": "1",
                    "competition": "old-comp",
                    "target": "old_target",
                    "raw_dir": "/tmp/old",
                }),
                encoding="utf-8",
            )
            with (
                mock.patch.object(ingest, "DATA_INTERIM", interim),
                mock.patch.object(ingest, "DATA_RAW", Path("/tmp/new")),
                mock.patch.object(ingest, "COMP", "new-comp"),
                mock.patch.object(ingest, "TARGET", "new_target"),
            ):
                with self.assertRaisesRegex(ValueError, "stale interim cache"):
                    ingest._assert_interim_cache_current()


if __name__ == "__main__":
    unittest.main()
