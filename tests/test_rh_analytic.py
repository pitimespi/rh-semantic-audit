"""RH-only tests of the analytic bridge fixture and source-line evidence."""
import unittest
from pathlib import Path

from semantic_graph.core import load, validate, ancestors
from tools.rh_analytic_check import source_line_checks

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "rh_analytic_bridge.json"


class AnalyticBridgeTests(unittest.TestCase):
    def test_graph_is_well_formed(self):
        graph = load(FIXTURE)
        self.assertEqual(validate(graph), [])
        self.assertEqual(len(graph["nodes"]), 8)
        self.assertEqual(len(graph["edges"]), 7)
        self.assertTrue(all(e["kind"] == "source_reference" for e in graph["edges"]))

    def test_ancestors_show_analytic_proof_composition(self):
        graph = load(FIXTURE)
        expected = {"hypsE2", "plugAll", "plugWin", "zeroFree",
                    "shapeWin", "supplyChi", "imprimitive"}
        self.assertEqual(set(ancestors(graph, "everyE2")), expected)

    def test_citation_line_checks_with_synthetic_sources(self):
        graph = load(FIXTURE)
        sources = {}
        by_id = {n["id"]: n for n in graph["nodes"]}
        for edge in graph["edges"]:
            src = edge["evidence"]["source"]
            line = int(src["url"].split("#L")[-1])
            lines = sources.setdefault(src["path"], [""] * 100)
            short = by_id[edge["from"]]["symbol"].split(".")[-1]
            # Every edge has a unique (path, line), except plugWin/imprimitive
            # share one line, and supplyChi/shapeWin share another.
            lines[line - 1] += " " + short
        sources = {k: "\n".join(v) for k, v in sources.items()}
        verdicts = source_line_checks(graph, sources)
        self.assertEqual(len(verdicts), 7)
        self.assertTrue(all(r["passed"] for r in verdicts), verdicts)

        path = graph["edges"][0]["evidence"]["source"]["path"]
        sources[path] = sources[path].replace("hypsE₂", "misleadingName", 1)
        verdicts = source_line_checks(graph, sources)
        self.assertFalse(verdicts[0]["passed"])

    def test_checker_rejects_wrong_origin(self):
        graph = load(FIXTURE)
        graph["project"]["revision"] = "0" * 40
        results = source_line_checks(graph, {})
        self.assertIn("Unrecognized repository", results[0]["error"])

    def test_no_claim_about_central_wrapper(self):
        graph = load(FIXTURE)
        self.assertNotIn("every_character_of_theta_integrals_local_matching",
                         {n["symbol"] for n in graph["nodes"]})
        self.assertIn("not yet been independently established",
                      graph["project"]["scope_note"])


if __name__ == "__main__":
    unittest.main()
