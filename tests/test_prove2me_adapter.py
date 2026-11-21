"""Offline Prove2me adapter tests, no network requests and no live credentials."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from semantic_graph.core import load, render_markdown, validate
from semantic_graph.prove2me import (
    add_decompositions, bind_theorem_details, fetch_readonly, link_proposal,
    lookup_theorem_exact, snapshot_hash, valid_uuid, exchange_api_key,
    access_token_from_environment,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "examples" / "bitcoin_supply.json"
LINKED = ROOT / "examples" / "bitcoin_supply_proposal_linked.json"
TID_SUBSIDY = "00000000-0000-4000-8000-000000000001"
TID_SUPPLY = "00000000-0000-4000-8000-000000000002"
SID = "00000000-0000-4000-8000-000000000003"


def sample_details():
    return [
        {
            "theorem_id": TID_SUBSIDY,
            "theorem_name": "BitcoinSubsidy.issuance_bound",
            "formal_statement": "theorem BitcoinSubsidy.issuance_bound ... := by sorry",
            "mathlib_rev": "0df444a3",
            "status": "Proved",
        },
        {
            "theorem_id": TID_SUPPLY,
            "theorem_name": "BitcoinSupply.supply_bound",
            "formal_statement": "theorem BitcoinSupply.supply_bound ... := by sorry",
            "mathlib_rev": "0df444a3",
            "status": "Proved",
        },
    ]


class Prove2meAdapterTests(unittest.TestCase):

    def test_real_pinned_proposal_item_ids(self):
        g = load(LINKED)
        self.assertEqual(validate(g), [])
        names = {n["symbol"]: n for n in g["nodes"]}
        n = names["BitcoinSupply.supply_bound"]
        self.assertEqual(n["proposal_record"]["proposal_item_id"],
                         "faa28708-d43f-446f-b6fc-16789c6befd2")
        self.assertIs(n["proposal_record"]["id_is_a_theorem_id"], False)
        self.assertEqual(n["proposal_record"]["repository_reported_submission_status"], "ACCEPTED")
        self.assertNotIn("theorem_record", n)

    def test_link_proposal_from_offline_source(self):
        g = load(BASE)
        proposal = {"proposal_id": "00000000-0000-4000-8000-000000000004",
                    "items": {"BitcoinSupply.supply_bound": "00000000-0000-4000-8000-000000000005",
                              "Not.In.Graph": "00000000-0000-4000-8000-000000000006"}}
        out, summary = link_proposal(g, proposal, {"BitcoinSupply.supply_bound": "ACCEPTED"})
        self.assertEqual(summary["matched"], ["BitcoinSupply.supply_bound"])
        self.assertEqual(summary["not_in_graph"], ["Not.In.Graph"])
        self.assertEqual(validate(out), [])
        self.assertNotIn("theorem_record", next(n for n in out["nodes"] if n["id"] == "supply_bound"))
        self.assertIn("proposal-item ID (not theorem ID)", render_markdown(out))

    def test_reject_misattributed_proposal_id(self):
        g = load(LINKED)
        n = next(x for x in g["nodes"] if x["id"] == "supply_bound")
        n["proposal_record"]["id_is_a_theorem_id"] = True
        self.assertTrue(any("NOT theorem_id" in x for x in validate(g)))
        n["proposal_record"]["id_is_a_theorem_id"] = False
        n["proposal_record"]["theorem_id"] = TID_SUPPLY
        self.assertTrue(any("conflates theorem_id" in x for x in validate(g)))

    def test_bind_actual_theorem_details(self):
        graph, names = bind_theorem_details(load(LINKED), sample_details())
        self.assertEqual(validate(graph), [])
        self.assertEqual(names, ["BitcoinSubsidy.issuance_bound", "BitcoinSupply.supply_bound"])
        sb = next(n for n in graph["nodes"] if n["id"] == "supply_bound")
        self.assertEqual(sb["theorem_record"]["theorem_id"], TID_SUPPLY)
        self.assertNotEqual(sb["proposal_record"]["proposal_item_id"], TID_SUPPLY)
        self.assertIn("theorem ID (from cached API response)", render_markdown(graph))
        self.assertEqual(sb["theorem_record"]["endpoint"],
                         "https://prove2.me/api/v1/theorems/" + TID_SUPPLY)

    def test_reject_ambiguous_theorem_name(self):
        x = sample_details()
        x[1]["theorem_name"] = "Unrecognized.GhostTheorem"
        with self.assertRaisesRegex(ValueError, "unknown theorem name"):
            bind_theorem_details(load(BASE), x)

    def test_reject_theorem_id_collision(self):
        x = sample_details()
        x[1]["theorem_id"] = TID_SUBSIDY
        with self.assertRaises(ValueError):
            bind_theorem_details(load(BASE), x)

    def test_platform_decomposition_is_not_kernel_dep(self):
        graph, _ = bind_theorem_details(load(LINKED), sample_details())
        response = {
            "decompositions": [
                {"submission_id": SID, "children": [
                    {"theorem_id": TID_SUBSIDY, "theorem_name": "BitcoinSubsidy.issuance_bound", "status": "Proved", "ordinal": 0},
                    {"theorem_id": "00000000-0000-4000-8000-000000000007",
                     "theorem_name": "Unknown.theorem", "status": "Open", "ordinal": 1},
                    {"definition_id": "00000000-0000-4000-8000-000000000008",
                     "definition_name": "SomeDefinition", "ordinal": 2},
                ]}
            ]
        }
        out, summary = add_decompositions(graph, "supply_bound", response)
        self.assertEqual(len(summary["added"]), 1)
        self.assertEqual(len(summary["unresolved"]), 2)
        self.assertEqual(validate(out), [])
        e = next(e for e in out["edges"] if e["kind"] == "platform_decomposition")
        self.assertEqual(e["from"], "subsidy_cap")
        self.assertEqual(e["to"], "supply_bound")
        self.assertEqual(e["evidence"]["api"]["snapshot_sha256"], snapshot_hash(response))
        self.assertEqual(e["semantic"]["review_status"], "draft")
        self.assertNotEqual(e["kind"], "kernel_dependency")
        again, summary2 = add_decompositions(out, "supply_bound", response)
        self.assertEqual(summary2["added"], [])
        self.assertEqual(len(again["edges"]), len(out["edges"]))

    def test_platform_response_needs_real_theorem_id(self):
        with self.assertRaisesRegex(ValueError, "actual theorem_id"):
            add_decompositions(load(LINKED), "supply_bound", {"decompositions": []})

    def test_proposal_items_are_not_usable_as_theorem_ids(self):
        g = load(LINKED)
        p = next(n["proposal_record"] for n in g["nodes"] if n["id"] == "supply_bound")
        self.assertNotIn("theorem_id", p)
        self.assertFalse(p["id_is_a_theorem_id"])

    def test_api_fetch_is_get_and_no_secret_logged(self):
        class FakeResponse:
            headers = {"Content-Type": "application/json"}
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, *args):
                return b'{"theorem_id":"00000000-0000-4000-8000-000000000002"}'

        def fake_urlopen(request, timeout=None):
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual(request.full_url,
                             "https://prove2.me/api/v1/theorems/" + TID_SUPPLY)
            self.assertEqual(request.get_header("Authorization"), "Bearer ephemeral-token")
            return FakeResponse()

        class FakeOpener:
            def open(self, request, timeout=None):
                return fake_urlopen(request, timeout)

        with mock.patch("semantic_graph.prove2me.urllib.request.build_opener", return_value=FakeOpener()) as build:
            response = fetch_readonly(TID_SUPPLY, "theorem", "ephemeral-token")
            self.assertEqual(build.call_args.args[0].__class__.__name__, "_NeverRedirect")
        self.assertEqual(response["theorem_id"], TID_SUPPLY)

    def test_exchange_api_key_only_posts_to_documented_endpoint(self):
        class Response:
            headers = {"Content-Type": "application/json"}
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, *args):
                return b'{"access_token":"short-lived-example","version":"0.8.1"}'

        class Opener:
            def open(self, request, timeout=None):
                self_ref.assertEqual(request.get_method(), "POST")
                self_ref.assertEqual(request.full_url, "https://prove2.me/api/v1/agent/refresh")
                self_ref.assertEqual(request.get_header("Content-type"), "application/json")
                self_ref.assertEqual(json.loads(request.data), {"api_key": "p2m_test-only"})
                return Response()

        self_ref = self
        with mock.patch("semantic_graph.prove2me.urllib.request.build_opener", return_value=Opener()) as opener:
            token = exchange_api_key("p2m_test-only")
            self.assertEqual(opener.call_args.args[0].__class__.__name__, "_NeverRedirect")
        self.assertEqual(token, "short-lived-example")

    def test_environment_prefers_access_token_and_never_echoes_key(self):
        with mock.patch("semantic_graph.prove2me.exchange_api_key", return_value="temporary") as exchange:
            token = access_token_from_environment({"PROVE2ME_API_KEY": "p2m_secret-only"})
            self.assertEqual(token, "temporary")
            exchange.assert_called_once_with("p2m_secret-only")
            token = access_token_from_environment({
                "PROVE2ME_API_KEY": "p2m_secret-only",
                "PROVE2ME_ACCESS_TOKEN": "provided-bearer",
            })
            self.assertEqual(token, "provided-bearer")
            exchange.assert_called_once()

    def test_rejects_missing_and_malformed_keys(self):
        for key in ("", "dummy", "p2m_bad\nheader"):
            with self.subTest(key=repr(key)):
                with self.assertRaises(ValueError):
                    exchange_api_key(key)
        with self.assertRaisesRegex(ValueError, "Set PROVE2ME_ACCESS_TOKEN or PROVE2ME_API_KEY"):
            access_token_from_environment({})

    def test_api_request_rejects_non_uuid(self):
        with self.assertRaises(ValueError):
            fetch_readonly("../../secrets", "theorem", "token")
        with self.assertRaises(ValueError):
            fetch_readonly(TID_SUPPLY, "unknown", "token")


    def test_lookup_exact_name_rejects_ambiguous_matches(self):
        name = "BitcoinSupply.supply_bound"
        search = {"theorems": [
            {"theorem_id": TID_SUPPLY, "theorem_name": name},
            {"theorem_id": "00000000-0000-4000-8000-000000000009", "theorem_name": name},
        ]}
        with mock.patch("semantic_graph.prove2me._get_json", return_value=search):
            with self.assertRaisesRegex(ValueError, "exactly one"):
                lookup_theorem_exact(name, "ephemeral-token")

    def test_lookup_exact_name_full_detail(self):
        name = "BitcoinSupply.supply_bound"
        response = {"theorem_id": TID_SUPPLY, "theorem_name": name,
                    "formal_statement": "theorem BitcoinSupply.supply_bound : True := by sorry"}
        def fake_get(url, token):
            self.assertEqual(token, "ephemeral-token")
            if "?q=" in url:
                return {"theorems": [response, {"theorem_name": "Other.name"}]}
            self.assertEqual(url, "https://prove2.me/api/v1/theorems/" + TID_SUPPLY)
            return response
        with mock.patch("semantic_graph.prove2me._get_json", side_effect=fake_get):
            self.assertEqual(lookup_theorem_exact(name, "ephemeral-token"), response)

    def test_no_network_access_without_token(self):
        with self.assertRaisesRegex(ValueError, "PROVE2ME_ACCESS_TOKEN"):
            fetch_readonly(TID_SUPPLY, "theorem", "")

    def test_digest_stable_for_key_order(self):
        self.assertEqual(snapshot_hash({"b": 2, "a": 1}),
                         snapshot_hash({"a": 1, "b": 2}))


if __name__ == "__main__":
    unittest.main()
