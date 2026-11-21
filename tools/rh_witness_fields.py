"""RH-only audit of the 46-field global hypothesis witness.

Checks the named field correspondence between the pinned HypsAlt structure
and the explicit record constructed in nonempty_hyps_of_allRows_alt.

NOT Lean elaboration, kernel verification, proof-term inspection or a
mathematical validity check. The JSON ledger stores only field names,
source locations and syntactic construction categories, not Lean source.
"""
import argparse
import collections
import json
import re
import urllib.request
from pathlib import Path

REPOSITORY = "Deicyde/riemann-hypothesis"
PIN = "e50d09817ad81469f737e8f637561e6ccf86c670"
PREFIX = "src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/"
FILES = {"definition": PREFIX + "Hyps.lean", "constructor": PREFIX + "NonemptyHypsOfAllRows.lean",
         "row": PREFIX + "AllRows.lean"}
EXPECTED_COUNT = 46
EXPECTED_ROW_COUNT = 26
# Accept Unicode identifiers (including 𝒜, σ) without assuming ASCII-only Lean.
FIELD = re.compile(r"^  ([^\s:]+)\s*:\s")
ASSIGN = re.compile(r"^    ([^\s:]+)\s*:=\s*(.*)$")


def parse_structure(source):
    lines = source.splitlines()
    starts = [i for i, line in enumerate(lines)
              if line.startswith("structure HypsAlt ") and ": Type 1 where" in line]
    if len(starts) != 1:
        raise ValueError("Expected one HypsAlt : Type 1 structure")
    result = []
    for index in range(starts[0] + 1, len(lines)):
        line = lines[index]
        if line.startswith("end GlobalTheory.Fc"):
            break
        match = FIELD.match(line)
        if match:
            result.append((match.group(1), index + 1))
    if len({name for name, _ in result}) != len(result):
        raise ValueError("Duplicate HypsAlt field names")
    return result


def parse_allrows(source):
    """Read 26 named fields of the upstream AllRowsAlt : Prop record."""
    lines = source.splitlines()
    markers = [i for i, line in enumerate(lines) if line.startswith("structure AllRowsAlt ")]
    if len(markers) != 1 or ": Prop where" not in "\n".join(lines[markers[0]:markers[0] + 3]):
        raise ValueError("Expected one AllRowsAlt : Prop structure")
    fields = []
    for index in range(markers[0] + 1, len(lines)):
        if lines[index].startswith("end GlobalTheory.Fc"):
            break
        match = FIELD.match(lines[index])
        if match:
            fields.append((match.group(1), index + 1))
    if len({k for k, _ in fields}) != len(fields):
        raise ValueError("Duplicate upstream AllRowsAlt fields")
    return fields


def parse_constructor(source):
    lines = source.splitlines()
    starts = [i for i, line in enumerate(lines)
              if line.strip() == "exact ⟨{"]
    if len(starts) != 1:
        raise ValueError("Expected one explicit final HypsAlt constructor")
    result = []
    closed = False
    for index in range(starts[0] + 1, len(lines)):
        line = lines[index]
        match = ASSIGN.match(line)
        if match:
            name, expr = match.groups()
            result.append((name, index + 1, expr))
        if "}⟩" in line:
            closed = True
            break
    if not closed:
        raise ValueError("HypsAlt constructor not closed")
    if len({name for name, _, _ in result}) != len(result):
        raise ValueError("Duplicate assigned HypsAlt fields")
    return result


def classify(name, rhs):
    expr = rhs.strip().removesuffix("}⟩").strip()
    if "Classical.choice" in expr:
        return "classical_choice"
    if "Closed.sub" in expr:
        return "closed_restriction"
    if expr.startswith("fun "):
        return "lambda"
    if expr == name or expr.startswith(name + " "):
        return "pass_through"
    return "derived"


def inspect(definition, constructor):
    declared = parse_structure(definition)
    assigned = parse_constructor(constructor)
    if len(declared) != EXPECTED_COUNT:
        raise ValueError(f"Unexpected HypsAlt field count: {len(declared)}")
    names = [x[0] for x in declared]
    other = [x[0] for x in assigned]
    if names != other:
        missing = sorted(set(names) - set(other))
        extra = sorted(set(other) - set(names))
        raise ValueError(f"HypsAlt constructor drift: missing={missing}, extra={extra}, order_matches={names == other}")
    return [
        {
            "field": name,
            "declaration_line": declaration_line,
            "constructor_line": assigned[i][1],
            "construction_kind": classify(name, assigned[i][2]),
        }
        for i, (name, declaration_line) in enumerate(declared)
    ]


def validate_ledger(ledger, actual):
    if ledger.get("schema_version") != "rh-hypsalt-fields/v1":
        raise ValueError("Unrecognized field-ledger schema")
    if ledger.get("source_repo") != REPOSITORY or ledger.get("commit") != PIN:
        raise ValueError("Ledger provenance does not match pinned RH source")
    if ledger.get("declaration_path") != FILES["definition"] or ledger.get("constructor_path") != FILES["constructor"]:
        raise ValueError("Ledger file paths do not match allowlist")
    claimed = ledger.get("fields")
    if not isinstance(claimed, list) or len(claimed) != EXPECTED_COUNT:
        raise ValueError("Ledger must contain 46 fields")
    for i, field in enumerate(actual):
        item = claimed[i]
        for key, value in field.items():
            if item.get(key) != value:
                raise ValueError(f"Field {i + 1}: {key} mismatches pinned Lean source")
        for key, path, linekey in [
            ("definition_url", FILES["definition"], "declaration_line"),
            ("assignment_url", FILES["constructor"], "constructor_line"),
        ]:
            expected = f"https://github.com/{REPOSITORY}/blob/{PIN}/{path}#L{field[linekey]}"
            if item.get(key) != expected:
                raise ValueError(f"Field {i + 1}: {key} points to wrong source line")
        if item.get("review_status") != "syntax_only":
            raise ValueError("Field review status is not warranted by source-only inspection")
    return collections.Counter(x["construction_kind"] for x in actual)


def validate_row_package(ledger, row_source, witness_fields):
    record = ledger.get("row_package")
    if not isinstance(record, dict):
        raise ValueError("Ledger missing upstream AllRowsAlt package")
    if record.get("type") != "GlobalTheory.Fc.AllRowsAlt : Prop" or record.get("source_path") != FILES["row"]:
        raise ValueError("Upstream row package provenance mismatch")
    rows = parse_allrows(row_source)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected 26 upstream row fields; found {len(rows)}")
    if not isinstance(record.get("fields"), list) or len(record["fields"]) != EXPECTED_ROW_COUNT:
        raise ValueError("Wrong upstream row field ledger length")
    names = {f["field"] for f in witness_fields}
    for i, (name, line) in enumerate(rows):
        item = record["fields"][i]
        if item.get("field") != name or item.get("declaration_line") != line:
            raise ValueError(f"Upstream row field {i + 1} mismatches pinned source")
        if item.get("declaration_url") != f"https://github.com/{REPOSITORY}/blob/{PIN}/{FILES['row']}#L{line}":
            raise ValueError("Row declaration URL is not source-pinned")
        if item.get("downstream_witness_field") != name or name not in names:
            raise ValueError(f"Row field {name} missing from downstream HypsAlt names")
        if item.get("correspondence_kind") != "name_only":
            raise ValueError("Source syntax does not justify stronger semantic equivalence")
    return len(rows)


def fetch_pinned(file):
    if file not in FILES.values():
        raise ValueError("File is outside the two-path allowlist")
    url = f"https://raw.githubusercontent.com/{REPOSITORY}/{PIN}/{file}"
    with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=45) as response:
        data = response.read(200_001)
    if len(data) > 200_000:
        raise ValueError("Source file exceeds configured size limit")
    return data.decode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-pinned", action="store_true")
    parser.add_argument("--ledger", type=Path, default=Path("examples/rh_witness_fields.json"))
    args = parser.parse_args(argv)
    if not args.fetch_pinned:
        parser.error("Use --fetch-pinned; no Lean code is executed")
    actual = inspect(fetch_pinned(FILES["definition"]), fetch_pinned(FILES["constructor"]))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    counters = validate_ledger(ledger, actual)
    upstream = validate_row_package(ledger, fetch_pinned(FILES["row"]), actual)
    print(json.dumps({
        "status": "source_syntax_only",
        "commit": PIN,
        "matched_fields": len(actual),
        "upstream_allrows_fields": upstream,
        "upstream_names_present_in_witness": upstream,
        "upstream_relation": "name_only",
        "missing": 0,
        "extra": 0,
        "classifications": dict(counters),
        "mathematical_verification": False,
        "lean_kernel_check": False,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
