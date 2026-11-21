#!/usr/bin/env python3
"""Check the *source text* at the pinned RH theorem interface, without Lean.

Downloads only three small/select files by immutable Git commit via
raw.githubusercontent.com. This is a syntactic scope check, not a proof,
typeclass/elaboration audit, or complete theorem-dependency extraction.
"""
import argparse
import json
import re
import urllib.request

PIN = "e50d09817ad81469f737e8f637561e6ccf86c670"
OWNER_REPO = "Deicyde/riemann-hypothesis"
PREFIX = "src/Development/AutomorphicArithmetic/"
PATHS = {
    "literature": PREFIX + "ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean",
    "main": PREFIX + "CharacterBoxes/MainConclusion.lean",
    "rec": PREFIX + "Foundations/LocalLanglands/LocalCentralUnits/RecTExists.lean",
    "row": PREFIX + "Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean",
    "every": PREFIX + "CharacterBoxes/EveryCharacter.lean",
}
EXPECTED_FIELDS = [
    ("caraianiLocalGlobalDual", "_root_.UpperTheory.One.M.Row"),
    ("localLanglandsExists", "_root_.UpperTheory.Zero.LLC.RecTExists"),
    ("galoisRepOfPolarizedPairLit", "_root_.UpperTheory.One.M.Row"),
]


def parse_fields(source):
    """Return the field names and types of this *specific* Lean Prop structure."""
    lines = source.splitlines()
    marker = "structure UpperTheory.LiteratureTheorems.OpenLiteratureStatements : Prop where"
    matches = [i for i, line in enumerate(lines) if line.strip() == marker]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one OpenLiteratureStatements declaration; found {len(matches)}")
    fields = []
    for line in lines[matches[0] + 1:]:
        if not line.strip() or line.lstrip().startswith("--"):
            continue
        m = re.match(r"^  ([A-Za-z_][A-Za-z_0-9]*)\s*:\s*(.*?)\s*$", line)
        if m is None:
            break
        fields.append((m.group(1), m.group(2)))
    return fields


def inspect_sources(sources):
    """Return public, non-secret status report; no source files copied."""
    problems = []
    missing = set(PATHS) - set(sources)
    if missing:
        return {"pinned_commit": PIN, "passed": False,
                "problems": ["Missing sources: " + ", ".join(sorted(missing))]}
    try:
        fields = parse_fields(sources["literature"])
    except ValueError as err:
        fields = []
        problems.append(str(err))
    if fields != EXPECTED_FIELDS:
        problems.append("OpenLiteratureStatements field names/types differ from the three expected fields")
    checks = [
        ("main", "⟨h, UpperTheory.Zero.LLC.recTExists, h⟩",
         "The main theorem no longer supplies the expected three-field tuple"),
        ("main", "(UpperTheory.One.vwin_of_row h)",
         "The main theorem no longer supplies VWin from the same Row0b input"),
        ("main", "theorem UpperTheory.FinalTheorems.everyCharacter_of_row",
         "The main theorem is not present"),
        ("rec", "theorem UpperTheory.Zero.LLC.recTExists :",
         "The named local Langlands existence theorem is not present"),
        ("rec", "UpperTheory.Zero.LLC.RecTExists := by",
         "The local Langlands existence theorem statement or proof introduction changed"),
        ("row", "theorem galoisLocalGlobalStrong_recParameter : UpperTheory.GalStar.Row0b recT :=",
         "The pinned Galois/row theorem type changed"),
        ("every", "def UpperTheory.EveryCharacter : Prop :=",
         "The every-character predicate declaration changed"),
        ("every", "DirichletCharacter.LFunction χ s ≠ 0",
         "The expected Dirichlet L-function nonvanishing target changed"),
    ]
    for name, needle, message in checks:
        if needle not in sources[name]:
            problems.append(message)
    return {
        "pinned_commit": PIN,
        "method": "source-text matching only, not Lean elaboration or kernel checking",
        "passed": not problems,
        "field_inventory": [{"field": k, "proposition": v} for k, v in fields],
        "problems": problems,
    }


def fetch_pinned(path):
    """Read-only, fixed-origin, immutable-commit raw source fetch."""
    if path not in PATHS.values():
        raise ValueError("Refusing source path outside the explicit RH review allowlist")
    url = f"https://raw.githubusercontent.com/{OWNER_REPO}/{PIN}/{path}"
    req = urllib.request.Request(url, headers={"Accept": "text/plain"}, method="GET")
    # No secret headers are sent. raw GitHub is unauthenticated.
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("Pinned RH source file exceeds 1 MB limit")
    return raw.decode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-pinned", action="store_true",
                        help="Fetch five allowlisted source files from the immutable GitHub commit")
    args = parser.parse_args(argv)
    if not args.fetch_pinned:
        parser.error("Use --fetch-pinned; this does not download or execute the complete Lean project")
    sources = {name: fetch_pinned(path) for name, path in PATHS.items()}
    result = inspect_sources(sources)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
