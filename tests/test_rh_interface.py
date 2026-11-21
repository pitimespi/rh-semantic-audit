"""RH-only semantic interface regression tests, using synthetic Lean text."""
import importlib.util
import unittest
from pathlib import Path

from semantic_graph.core import load, validate

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rh_interface_check",
    ROOT / "tools" / "rh_interface_check.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

LITERATURE = """section
structure UpperTheory.LiteratureTheorems.OpenLiteratureStatements : Prop where
  caraianiLocalGlobalDual : _root_.UpperTheory.One.M.Row
  localLanglandsExists : _root_.UpperTheory.Zero.LLC.RecTExists
  galoisRepOfPolarizedPairLit : _root_.UpperTheory.One.M.Row
theorem Test : True := by trivial
"""
SOURCES = {
    "literature": LITERATURE,
    "main": (
        "theorem UpperTheory.FinalTheorems.everyCharacter_of_row : UpperTheory.EveryCharacter :=\n"
        "  UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin "
        "⟨h, UpperTheory.Zero.LLC.recTExists, h⟩ (UpperTheory.One.vwin_of_row h)\n"
    ),
    "rec": "theorem UpperTheory.Zero.LLC.recTExists :\n    UpperTheory.Zero.LLC.RecTExists := by\n",
    "row": "theorem galoisLocalGlobalStrong_recParameter : UpperTheory.GalStar.Row0b recT :=",
    "every": "def UpperTheory.EveryCharacter : Prop :=\n  DirichletCharacter.LFunction χ s ≠ 0",
}


class RHInterfaceTests(unittest.TestCase):
    def test_exact_three_fields(self):
        self.assertEqual(audit.parse_fields(LITERATURE), audit.EXPECTED_FIELDS)
        self.assertEqual(audit.EXPECTED_FIELDS[0][1], audit.EXPECTED_FIELDS[2][1])

    def test_synthetic_interface_passes(self):
        r = audit.inspect_sources(SOURCES)
        self.assertTrue(r["passed"], r["problems"])
        self.assertEqual(len(r["field_inventory"]), 3)

    def test_additional_field_is_detected(self):
        changed = dict(SOURCES)
        changed["literature"] = LITERATURE.replace("theorem Test", "  unreviewedExtra : False\ntheorem Test")
        r = audit.inspect_sources(changed)
        self.assertFalse(r["passed"])
        self.assertTrue(any("field names/types differ" in x for x in r["problems"]))

    def test_missing_tuple_is_detected(self):
        changed = dict(SOURCES)
        changed["main"] = changed["main"].replace("recTExists, h", "recTExists, proof2")
        self.assertFalse(audit.inspect_sources(changed)["passed"])

    def test_source_fetch_allowlist(self):
        with self.assertRaisesRegex(ValueError, "allowlist"):
            audit.fetch_pinned("other-user/repo/secret.txt")

    def test_rh_semantic_graph_includes_exact_fields(self):
        graph = load(ROOT / "examples/rh_critical_path.json")
        self.assertEqual(validate(graph), [])
        literature = next(n for n in graph["nodes"] if n["id"] == "literature")
        fields = [x["name"] for x in literature["assumptions"]]
        self.assertEqual(fields[:3],
            ["O.caraianiLocalGlobalDual", "O.localLanglandsExists",
             "O.galoisRepOfPolarizedPairLit"])
        self.assertTrue(all(e["kind"] != "kernel_dependency" for e in graph["edges"]))


if __name__ == "__main__":
    unittest.main()
