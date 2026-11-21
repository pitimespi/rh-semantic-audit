"""Prove2me contribution publishing tests — all HTTP interactions are mocked."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from semantic_graph import publish

TID = "00000000-0000-4000-8000-000000000002"
SID = "00000000-0000-4000-8000-000000000003"
NAME = "BitcoinSupply.supply_lt_maxMoney"


def api_response(url, token):
    if url.endswith("/submissions?page=1"):
        return {"submissions": [{"id": SID, "theorem_id": TID, "status": "ACCEPTED"}], "total": 1}
    if url.startswith("https://prove2.me/api/v1/theorems/" + TID + "/submissions?"):
        return {"submissions": [{"id": SID, "theorem_id": TID, "status": "ACCEPTED",
                                 "explanation": ""}], "total": 1}
    raise AssertionError("Unexpected URL: " + url)


class PublishTests(unittest.TestCase):
    def test_resolve_uses_only_owned_accepted_submission(self):
        with mock.patch.object(publish, "lookup_theorem_exact", return_value={
            "theorem_id": TID, "theorem_name": NAME, "status": "Proved",
        }):
            with mock.patch.object(publish, "_get_json", side_effect=api_response):
                theorem, sid, existing = publish.resolve_owned_target(NAME, "bearer")
        self.assertEqual(theorem["theorem_name"], NAME)
        self.assertEqual(sid, SID)
        self.assertEqual(existing, "")

    def test_missing_ownership_cannot_patch(self):
        with mock.patch.object(publish, "lookup_theorem_exact", return_value={
            "theorem_id": TID, "theorem_name": NAME,
        }):
            with mock.patch.object(publish, "_get_json", return_value={
                "submissions": [{"id": SID, "theorem_id": TID, "status": "FAILED"}], "total": 1,
            }):
                with self.assertRaisesRegex(ValueError, "owned accepted submission"):
                    publish.resolve_owned_target(NAME, "bearer")

    def test_multiple_own_submissions_requires_disambiguation(self):
        second = "00000000-0000-4000-8000-000000000004"
        def data(url, token):
            if url.endswith("/submissions?page=1"):
                return {"submissions": [
                    {"id": SID, "theorem_id": TID, "status": "ACCEPTED"},
                    {"id": second, "theorem_id": TID, "status": "ACCEPTED"},
                ], "total": 2}
            return {"submissions": [{"id": SID, "theorem_id": TID,
                                     "status": "ACCEPTED", "explanation": ""}]}
        with mock.patch.object(publish, "lookup_theorem_exact", return_value={
            "theorem_id": TID, "theorem_name": NAME,
        }), mock.patch.object(publish, "_get_json", side_effect=data):
            with self.assertRaisesRegex(ValueError, "exactly one"):
                publish.resolve_owned_target(NAME, "bearer")
            _, sid, _ = publish.resolve_owned_target(NAME, "bearer", SID)
            self.assertEqual(sid, SID)

    def test_preview_never_applies_patch(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "explanation.md"
            file.write_text("A proof explanation.", encoding="utf-8")
            with mock.patch.object(publish, "access_token_from_environment", return_value="token"), \
                 mock.patch.object(publish, "resolve_owned_target", return_value=(
                     {"theorem_name": NAME, "theorem_id": TID, "status": "Proved"}, SID, ""
                 )), mock.patch.object(publish, "patch_explanation") as patched:
                rc = publish.main(["--theorem-name", NAME, "--explanation-file", str(file)])
                self.assertEqual(rc, 0)
                patched.assert_not_called()

    def test_apply_requires_exact_explicit_confirmed_submission(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "explanation.md"
            file.write_text("Reviewed explanation.", encoding="utf-8")
            with mock.patch.object(publish, "access_token_from_environment", return_value="token"), \
                 mock.patch.object(publish, "resolve_owned_target", return_value=(
                     {"theorem_name": NAME, "theorem_id": TID, "status": "Proved"}, SID, ""
                 )), mock.patch.object(publish, "patch_explanation") as patched:
                rc = publish.main(["--theorem-name", NAME, "--explanation-file", str(file),
                                   "--apply", "--confirm-submission-id", TID])
                self.assertEqual(rc, 2)
                patched.assert_not_called()
                patched.return_value = {"id": SID, "explanation": "Reviewed explanation."}
                rc = publish.main(["--theorem-name", NAME, "--explanation-file", str(file),
                                   "--apply", "--confirm-submission-id", SID])
                self.assertEqual(rc, 0)
                patched.assert_called_once_with(SID, "Reviewed explanation.", "token")

    def test_existing_explanation_requires_replace_existing(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "explanation.md"
            file.write_text("New explanation", encoding="utf-8")
            with mock.patch.object(publish, "access_token_from_environment", return_value="token"), \
                 mock.patch.object(publish, "resolve_owned_target", return_value=(
                     {"theorem_name": NAME, "theorem_id": TID}, SID, "Existing explanation"
                 )), mock.patch.object(publish, "patch_explanation") as patched:
                self.assertEqual(publish.main([
                    "--theorem-name", NAME, "--explanation-file", str(file)
                ]), 2)
                patched.assert_not_called()

    def test_patch_endpoint_and_payload_are_restricted(self):
        class Response:
            headers = {"Content-Type": "application/json"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, *args): return b'{"id":"00000000-0000-4000-8000-000000000003"}'

        class Opener:
            def open(self, request, timeout=None):
                self_ref.assertEqual(request.get_method(), "PATCH")
                self_ref.assertEqual(request.full_url, "https://prove2.me/api/v1/submissions/" + SID)
                self_ref.assertEqual(request.get_header("Authorization"), "Bearer token")
                self_ref.assertEqual(json.loads(request.data), {"explanation": "Text only"})
                return Response()

        self_ref = self
        with mock.patch.object(publish.urllib.request, "build_opener", return_value=Opener()) as build:
            result = publish.patch_explanation(SID, "Text only", "token")
            self.assertEqual(build.call_args.args[0].__class__.__name__, "_NeverRedirect")
        self.assertEqual(result["id"], SID)


if __name__ == "__main__":
    unittest.main()
