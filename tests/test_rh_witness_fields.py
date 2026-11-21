"""RH HypsAlt witness-field inventory regression tests (no Lean compiler)."""
import json
import unittest
from pathlib import Path

from tools.rh_witness_fields import (
    EXPECTED_COUNT,
    classify,
    inspect,
    parse_constructor,
    parse_structure,
    validate_ledger,
)

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "examples" / "rh_witness_fields.json"

STRUCT = """namespace GlobalTheory.Fc
structure HypsAlt (N : FamClass → Prop) (DR : DefiniteSideType) : Type 1 where
  𝒜 : FamClass
  σ : RawSel 𝒜
  hLit : LitThin
end GlobalTheory.Fc
"""
CONSTRUCTOR = """theorem sample := by
  exact ⟨{
    𝒜 := 𝒜
    σ := σ
    hLit := hLit }⟩
"""


class RHWitnessFieldTests(unittest.TestCase):
    def test_unicode_and_multiline_struct_fields(self):
        self.assertEqual(
            [name for name, _ in parse_structure(STRUCT)],
            ["𝒜", "σ", "hLit"],
        )
        self.assertEqual(
            [name for name, _, _ in parse_constructor(CONSTRUCTOR)],
            ["𝒜", "σ", "hLit"],
        )

    def test_missing_field_is_not_silent(self):
        incomplete = CONSTRUCTOR.replace("    σ := σ\n", "")
        with self.assertRaisesRegex(ValueError, "field count"):
            inspect(STRUCT, incomplete)

    def test_classification_of_explicit_choice_and_restriction(self):
        self.assertEqual(classify("selJ", "fun Fm => Classical.choice (h Fm)"), "classical_choice")
        self.assertEqual(classify("hn4", "Formalism.MainNotions.Pk.Closed.sub hn4 s1"), "closed_restriction")
        self.assertEqual(classify("hG", "hG"), "pass_through")
        self.assertEqual(classify("hRB", "fun Fm => hRB Fm"), "lambda")

    def test_ledger_is_pinned_and_has_all_46_names(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["fields"]), EXPECTED_COUNT)
        self.assertEqual(len({x["field"] for x in ledger["fields"]}), EXPECTED_COUNT)
        self.assertEqual(ledger["source_repo"], "Deicyde/riemann-hypothesis")
        self.assertTrue(all(x["review_status"] == "syntax_only" for x in ledger["fields"]))
        self.assertEqual(
            [x["field"] for x in ledger["fields"] if x["construction_kind"] == "classical_choice"],
            ["selJ"],
        )

    def test_checker_accepts_ledger_shape_with_extracted_source_facts(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        facts = [{key: record[key] for key in (
            "field", "declaration_line", "constructor_line", "construction_kind"
        )} for record in ledger["fields"]]
        counts = validate_ledger(ledger, facts)
        self.assertEqual(sum(counts.values()), EXPECTED_COUNT)
        self.assertEqual(counts["classical_choice"], 1)

    def test_checker_rejects_wrong_source_position(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        facts = [{key: record[key] for key in (
            "field", "declaration_line", "constructor_line", "construction_kind"
        )} for record in ledger["fields"]]
        facts[0]["constructor_line"] += 1
        with self.assertRaisesRegex(ValueError, "mismatches pinned"):
            validate_ledger(ledger, facts)


if __name__ == "__main__":
    unittest.main()
