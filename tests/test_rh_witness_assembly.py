"""RH witness assembly graph regression tests."""
import unittest
from pathlib import Path

from semantic_graph.core import ancestors, load, validate
from tools.rh_analytic_check import source_line_checks

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "examples" / "rh_witness_assembly.json"


class RHWitnessAssemblyTests(unittest.TestCase):
    def test_graph_schema_and_scope(self):
        graph = load(GRAPH)
        self.assertEqual(validate(graph), [])
        self.assertEqual(len(graph["nodes"]), 16)
        self.assertEqual(len(graph["edges"]), 15)
        self.assertTrue(all(e["kind"] == "source_reference" for e in graph["edges"]))
        self.assertNotIn("everyE₂", " ".join(n["symbol"] for n in graph["nodes"]))

    def test_underlying_constructors_are_explicit(self):
        graph = load(GRAPH)
        names = {node["id"]: node["symbol"] for node in graph["nodes"]}
        self.assertEqual(names["rowsWitness"],
                         "GlobalTheory.Fc.nonempty_hyps_of_allRows_alt")
        self.assertEqual(names["stage"],
                         "GlobalTheory.Fc.S0.StageU.hypotheses_nonempty_of_unramified_exponents_alt")
        upstream = set(ancestors(graph, "nonempty"))
        self.assertEqual(len(upstream), 15)
        self.assertIn("choose", upstream)
        self.assertIn("large", upstream)
        self.assertIn("allRows", upstream)

    def test_line_checker_finds_all_15_explicit_calls(self):
        graph = load(GRAPH)
        nodes = {n["id"]: n for n in graph["nodes"]}
        files = {}
        for edge in graph["edges"]:
            source = edge["evidence"]["source"]
            line = int(source["url"].split("#L")[-1])
            lines = files.setdefault(source["path"], [])
            if len(lines) < line:
                lines.extend([""] * (line - len(lines)))
            symbol = nodes[edge["from"]]["symbol"].split(".")[-1]
            lines[line - 1] += " " + symbol
        sources = {path: "\n".join(lines) for path, lines in files.items()}
        results = source_line_checks(graph, sources)
        self.assertEqual(len(results), 15)
        self.assertTrue(all(x["passed"] for x in results), results)

        first = graph["edges"][0]
        source = first["evidence"]["source"]
        sources[source["path"]] = sources[source["path"]].replace(
            nodes[first["from"]]["symbol"].split(".")[-1],
            "name_changed",
            1,
        )
        results = source_line_checks(graph, sources)
        self.assertFalse(results[0]["passed"])


if __name__ == "__main__":
    unittest.main()
