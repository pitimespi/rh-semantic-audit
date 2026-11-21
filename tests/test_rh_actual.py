"""Tests of the actual central seven-premise RH theorem graph."""
import unittest
from pathlib import Path

from semantic_graph.core import ancestors, load, validate
from tools.rh_analytic_check import source_line_checks

ROOT = Path(__file__).resolve().parents[1]
ACTUAL = ROOT / "examples" / "rh_actual_bridge.json"
OLDER = ROOT / "examples" / "rh_analytic_bridge.json"

EXPECTED = [
    "UnitaryGroupThirdPlaceHypotheses",
    "ThetaLocalInputs",
    "ThetaIntegralsAgree",
    "LocalMatching",
    "CovolumeBoundOfX",
    "RecTExists",
    "VWin",
]


class ActualCentralBridgeTests(unittest.TestCase):
    def test_graph_valid_and_explicit_hypotheses(self):
        graph = load(ACTUAL)
        self.assertEqual(validate(graph), [])
        t = next(n for n in graph["nodes"] if n["id"] == "thetaTarget")
        self.assertEqual(len(t["assumptions"]), 7)
        self.assertEqual(
            [a["meaning"] for a in t["assumptions"]], EXPECTED
        )

    def test_actual_and_older_bridge_are_different(self):
        actual = load(ACTUAL)
        older = load(OLDER)
        self.assertNotIn(
            "UpperTheory.Lit.everyE₂",
            {n["symbol"] for n in actual["nodes"]},
        )
        self.assertIn(
            "UpperTheory.Lit.everyE₂",
            {n["symbol"] for n in older["nodes"]},
        )
        self.assertIn("nonempty", ancestors(actual, "thetaTarget"))
        self.assertIn("greenEvery", ancestors(actual, "outer"))

    def test_all_edges_source_only(self):
        graph = load(ACTUAL)
        self.assertEqual(len(graph["edges"]), 11)
        self.assertTrue(all(e["kind"] == "source_reference" for e in graph["edges"]))

    def test_pinned_line_references_can_be_checked(self):
        graph = load(ACTUAL)
        by_id = {n["id"]: n for n in graph["nodes"]}
        lines_by_file = {}
        for edge in graph["edges"]:
            src = edge["evidence"]["source"]
            num = int(src["url"].rsplit("#L", 1)[1])
            lines = lines_by_file.setdefault(src["path"], [""] * 90)
            symbol = by_id[edge["from"]]["symbol"].split(".")[-1]
            lines[num - 1] += " " + symbol
        result = source_line_checks(
            graph, {k: "\n".join(v) for k, v in lines_by_file.items()}
        )
        self.assertEqual(len(result), 11)
        self.assertTrue(all(x["passed"] for x in result), result)


if __name__ == "__main__":
    unittest.main()
