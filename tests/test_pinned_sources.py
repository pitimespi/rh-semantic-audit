"""Static reference-checker tests (never execute Lean)."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from semantic_graph.cli import check_references
from semantic_graph.core import load


ROOT = Path(__file__).resolve().parents[1]


class PinnedSourceReferenceTests(unittest.TestCase):
    def test_references_only_at_explicit_source_lines(self):
        graph = load(ROOT / "examples" / "bitcoin_supply_proposal_linked.json")
        by_id = {n["id"]: n for n in graph["nodes"]}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            files = {}
            for e in graph["edges"]:
                if e["kind"] != "source_reference":
                    continue
                ref = e["evidence"]["source"]
                lineno = int(ref["url"].split("#L")[-1])
                content = files.setdefault(ref["path"], [""] * 330)
                content[lineno - 1] = "  have witness := " + by_id[e["from"]]["symbol"] + " S hR"
            for path, contents in files.items():
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("\n".join(contents) + "\n")
            with mock.patch("semantic_graph.cli.check_pin", return_value=root):
                report = check_references(graph, root)
                self.assertEqual(len(report), 3)
                self.assertTrue(all(r["status"] == "symbol_present_at_pinned_line" for r in report))
                graph["edges"][1]["evidence"]["source"]["url"] = graph["edges"][1]["evidence"]["source"]["url"].split("#")[0] + "#L999"
                bad = check_references(graph, root)
                self.assertTrue(any(r["status"] == "line_out_of_range" for r in bad))

    def test_imports_are_not_strong_source_edges(self):
        graph = load(ROOT / "examples" / "bitcoin_supply.json")
        self.assertEqual([e["id"] for e in graph["edges"] if e["kind"] == "import_candidate"],
                         ["b1", "b3"])
        self.assertEqual([e["id"] for e in graph["edges"] if e["kind"] == "source_reference"],
                         ["b2", "b4", "b5"])


if __name__ == "__main__":
    unittest.main()
