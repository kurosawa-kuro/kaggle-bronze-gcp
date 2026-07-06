import unittest

from runner.ops.submission_ledger import extract_run_id, message_with_run_id, parse_submissions_csv


class SubmissionLedgerTest(unittest.TestCase):
    def test_message_with_run_id_is_idempotent(self):
        msg = message_with_run_id("baseline", "run01")
        self.assertEqual(msg, "baseline [run_id=run01]")
        self.assertEqual(message_with_run_id(msg, "run01"), msg)

    def test_parse_kaggle_csv(self):
        text = (
            "ref,fileName,date,description,status,publicScore,privateScore\n"
            "53773424,submission.csv,2026-06-17 11:05:20.263000,"
            "baseline [run_id=run01],SubmissionStatus.COMPLETE,0.95812,0.95780\n"
        )
        rows = parse_submissions_csv(text, competition="playground")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["submission_ref"], "53773424")
        self.assertEqual(rows[0]["run_id"], "run01")
        self.assertEqual(rows[0]["competition"], "playground")
        self.assertEqual(rows[0]["public_lb"], 0.95812)
        self.assertEqual(rows[0]["private_lb"], 0.95780)

    def test_extract_run_id_returns_none_when_missing(self):
        self.assertIsNone(extract_run_id("manual web submission"))


if __name__ == "__main__":
    unittest.main()
