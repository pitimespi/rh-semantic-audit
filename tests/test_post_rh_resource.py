"""RH Prove2me reference-resource submission tests; no live HTTP traffic."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from semantic_graph import post_rh_resource as rh

MID = "00000000-0000-4000-8000-000000000043"
RID = "00000000-0000-4000-8000-000000000044"


class RHResourcePostingTests(unittest.TestCase):
    def test_resource_is_bounded_source_pinned_article(self):
        item = rh.load_resource()
        self.assertEqual(item["type"], "article")
        self.assertEqual(item["url"], rh.CANONICAL_URL)
        self.assertIn("NOT a proof", item["description"])

    def test_default_preview_never_reads_key_or_calls_network(self):
        with mock.patch.object(rh, "access_token_from_environment") as token, \
             mock.patch.object(rh, "_get_json") as request, \
             mock.patch.object(rh, "post_resource") as post:
            rc = rh.main([])
        self.assertEqual(rc, 0)
        token.assert_not_called()
        request.assert_not_called()
        post.assert_not_called()

    def test_exact_mission_name_and_target_both_required(self):
        expected = {"id": MID, "name": rh.MISSION_NAME, "visibility": "public",
                    "main_theorem": {"theorem_name": rh.THEOREM_NAME}}
        data = {"missions": [
            {"id": "00000000-0000-4000-8000-000000000001",
             "name": rh.MISSION_NAME,
             "main_theorem": {"theorem_name": "not_the_riemann_hypothesis"}},
            expected,
        ]}
        with mock.patch.object(rh, "_get_json", return_value=data):
            self.assertEqual(rh.get_exact_rh_mission("token")["id"], MID)
        with mock.patch.object(rh, "_get_json", return_value={"missions": [data["missions"][0]]}):
            with self.assertRaisesRegex(ValueError, "exactly one"):
                rh.get_exact_rh_mission("token")

    def test_requires_confirmation_even_with_apply(self):
        with mock.patch.object(rh, "access_token_from_environment") as token, \
             mock.patch.object(rh, "post_resource") as post:
            rc = rh.main(["--apply"])
        self.assertEqual(rc, 2)
        token.assert_not_called()
        post.assert_not_called()

    def test_duplicate_resource_url_prevents_second_post(self):
        with mock.patch.object(rh, "access_token_from_environment", return_value="token"), \
             mock.patch.object(rh, "get_exact_rh_mission", return_value={"id": MID}), \
             mock.patch.object(rh, "read_existing_resources",
                               return_value=[{"id": RID, "url": rh.CANONICAL_URL}]), \
             mock.patch.object(rh, "post_resource") as post:
            self.assertEqual(rh.main([
                "--apply", "--confirm-mission-slug", rh.MISSION_SLUG,
            ]), 0)
            post.assert_not_called()

    def test_single_post_only_when_exact_mission_confirmed(self):
        with mock.patch.object(rh, "access_token_from_environment", return_value="token"), \
             mock.patch.object(rh, "get_exact_rh_mission", return_value={"id": MID}), \
             mock.patch.object(rh, "read_existing_resources", return_value=[]), \
             mock.patch.object(rh, "post_resource",
                               return_value={"id": RID, "url": rh.CANONICAL_URL}) as post:
            self.assertEqual(rh.main([
                "--apply", "--confirm-mission-slug", rh.MISSION_SLUG
            ]), 0)
            post.assert_called_once_with(MID, "token", rh.load_resource())

    def test_post_endpoint_and_body_exclude_credential(self):
        resource = rh.load_resource()
        class Response:
            status = 201
            headers = {"Content-Type": "application/json"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, n): return json.dumps({"resource": {"id": RID, **resource}}).encode()

        class Opener:
            def open(self, req, timeout=None):
                self_ref.assertEqual(req.get_method(), "POST")
                self_ref.assertEqual(req.full_url, f"https://prove2.me/api/v1/missions/{MID}/resources")
                self_ref.assertEqual(json.loads(req.data), resource)
                self_ref.assertEqual(req.get_header("Authorization"), "Bearer secret-token")
                self_ref.assertNotIn("secret-token", req.full_url)
                return Response()

        self_ref = self
        with mock.patch.object(rh.urllib.request, "build_opener", return_value=Opener()) as opener:
            res = rh.post_resource(MID, "secret-token", resource)
            self.assertEqual(opener.call_args.args[0].__class__.__name__, "_NeverRedirect")
        self.assertEqual(res["id"], RID)

    def test_unapproved_payload_cannot_be_published(self):
        resource = rh.load_resource()
        resource["description"] = "unreviewed substitute"
        with self.assertRaisesRegex(ValueError, "modified/unknown"):
            rh.post_resource(MID, "test", resource)


if __name__ == "__main__":
    unittest.main()
