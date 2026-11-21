"""Source-line check for the RH Minkowski conditional: synthetic tests only."""
import unittest
from tools.rh_minkowski_check import CHECKS, inspect, fetch_pinned


def synthetic_sources():
    result = {}
    for path, lineno, snippet in CHECKS.values():
        lines = result.setdefault(path, [])
        if len(lines) < lineno:
            lines.extend([""] * (lineno - len(lines)))
        lines[lineno - 1] += " " + snippet
    return {path: "\n".join(lines) for path, lines in result.items()}


class RHMinkowskiChecks(unittest.TestCase):
    def test_all_eight_source_correspondences(self):
        s = synthetic_sources()
        result = inspect(s)
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["checks"]), 8)
        self.assertFalse(result["lean_elaboration"])
        self.assertFalse(result["kernel_verification"])

    def test_missing_supplier_is_detected(self):
        s = synthetic_sources()
        row = CHECKS["antecedent_discharge"]
        s[row[0]] = s[row[0]].replace(row[2], "hEx unknown_source")
        result = inspect(s)
        self.assertFalse(result["passed"])
        self.assertFalse(next(x for x in result["checks"] if x["id"] == "antecedent_discharge")["passed"])

    def test_source_line_is_essential(self):
        s = synthetic_sources()
        row = CHECKS["named_supplier"]
        s[row[0]] = "\n" + s[row[0]]
        self.assertFalse(inspect(s)["passed"])

    def test_no_arbitrary_source_path_fetch(self):
        with self.assertRaisesRegex(ValueError, "allowlist"):
            fetch_pinned("secrets.txt")


if __name__ == "__main__":
    unittest.main()
