"""Tests use the actual checked-in prototypes; no GitHub network or Lean build needed."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from semantic_graph.core import (
    SCHEMA, ancestors, import_candidates, load, render_markdown, render_mermaid, validate,
)


ROOT = Path(__file__).resolve().parents[1]
BITCOIN = ROOT / "examples" / "bitcoin_supply.json"
RH = ROOT / "examples" / "rh_critical_path.json"


class TestSemanticGraph(unittest.TestCase):
    def test_both_graphs_valid(self):
        for path in (BITCOIN, RH):
            with self.subTest(path=path):
                graph = load(path)
                self.assertEqual(graph["schema_version"], SCHEMA)
                self.assertEqual(validate(graph), [])

    def test_ancestors(self):
        graph = load(BITCOIN)
        self.assertEqual(ancestors(graph, "supply_cap"),
                         ["block_supply", "reachable", "subsidy_cap", "supply_bound"])
        with self.assertRaises(KeyError):
            ancestors(graph, "not-a-node")

    def test_mermaid_renders_kind(self):
        graph = load(BITCOIN)
        output = render_mermaid(graph)
        self.assertIn("import only", output)
        self.assertIn("supply_bound", output)
        self.assertNotIn("kernel trace", output)

    def test_review_report_discloses_limits(self):
        graph = load(RH)
        output = render_markdown(graph, "headline")
        self.assertIn("no independent proof-term verification", output)
        self.assertIn("draft", output)
        self.assertIn("RiemannHypothesis", output)

    def test_reject_unsupported_kernel_claim(self):
        graph = load(BITCOIN)
        graph["edges"][0]["kind"] = "kernel_dependency"
        self.assertTrue(any("kernel_dependency needs" in x for x in validate(graph)))

    def test_disclose_semantic_review(self):
        graph = load(BITCOIN)
        graph["edges"][0]["semantic"]["review_status"] = "independent_review"
        self.assertTrue(any("two distinct reviewers" in x for x in validate(graph)))
        graph["edges"][0]["semantic"]["reviewers"] = ["reader-1", "reader-2"]
        self.assertEqual(validate(graph), [])

    def test_reject_unpinned_source(self):
        graph = load(BITCOIN)
        graph["nodes"][0]["source"]["url"] = "https://github.com/pitimespi/prove2me/blob/main/foo.lean"
        self.assertTrue(any(".source needs path" in x for x in validate(graph)))

    def test_cycle_and_dangling_ref(self):
        graph = load(BITCOIN)
        graph["edges"][0]["from"] = "supply_cap"
        graph["edges"][0]["to"] = "subsidy_cap"
        self.assertTrue(any("directed cycle" in x for x in validate(graph)))
        graph = load(BITCOIN)
        graph["edges"][0]["to"] = "missing"
        self.assertTrue(any("unknown node" in x for x in validate(graph)))

    def test_duplicate_ids(self):
        graph = load(RH)
        graph["nodes"][1]["id"] = graph["nodes"][0]["id"]
        self.assertTrue(any("duplicated" in x for x in validate(graph)))

    def test_import_candidates_are_not_dependencies(self):
        lean = ("import Definitions.Def_BitcoinSupply\n"
                "import Theorems.Thm_BitcoinSubsidy_issuance_bound\n"
                "import Theorems.Thm_BitcoinSupply_block_supply\n"
                "-- import Theorems.Thm_fake\n")
        self.assertEqual(
            import_candidates(lean),
            ["Theorems.Thm_BitcoinSubsidy_issuance_bound",
             "Theorems.Thm_BitcoinSupply_block_supply"],
        )

    def test_reject_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text('{"x":1,"x":2}')
            with self.assertRaises(ValueError):
                load(path)


if __name__ == "__main__":
    unittest.main()
