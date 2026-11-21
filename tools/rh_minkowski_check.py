"""Audit a single conditional-discharge step in the pinned RH source.

Checks exact literal Lean source lines at immutable GitHub commit; not a Lean
kernel check, not definitional equivalence and not a proof of RH.
"""
import argparse
import json
import urllib.request

PIN = "e50d09817ad81469f737e8f637561e6ccf86c670"
REPO = "Deicyde/riemann-hypothesis"
BASE = "src/Development/AutomorphicArithmetic/"
THIRD = BASE + "ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/"
CHECKS = {
    "classSel_conditional": (
        BASE + "CharacterBoxes/ClassSel.lean", 14,
        "DC.MinkDiv → ExD 𝒜 cT",
    ),
    "witness_field_conditional": (
        THIRD + "Hyps.lean", 26,
        "hEx : MinkDiv → UpperTheory.Top.ExS 𝒜 cT",
    ),
    "witness_field_assignment": (
        THIRD + "NonemptyHypsOfAllRows.lean", 59,
        "hEx := fun hM la G hla hH =>",
    ),
    "downstream_shape_application": (
        THIRD + "TopShape.lean", 50,
        "GlobalTheory.Top.designExists_of_tuSize_aux4n_litThin",
    ),
    "antecedent_discharge": (
        THIRD + "LinkEx.lean", 35,
        "hEx minkowski_bound_rat",
    ),
    "named_supplier": (
        "src/Formalism/PeriodIntegrals/OrbitalBoundsConclusion/MinkowskiQ.lean",
        6, "theorem minkowski_bound_rat : PI.MinkowskiBoundQ := PI.MkQ.minkowskiBoundQ",
    ),
    "upstream_minkowski_theorem": (
        "src/Formalism/PeriodIntegrals/UnitaryGroupMassFormula/MinkowskiTorsionFree/Lattice.lean",
        124, "theorem minkowskiBoundQ : PI.MinkowskiBoundQ := by",
    ),
    "upstream_divisibility_application": (
        "src/Formalism/PeriodIntegrals/UnitaryGroupMassFormula/MinkowskiTorsionFree/Lattice.lean",
        129, "exact card_dvd_minkowskiNumber",
    ),
}


def inspect(sources):
    checks = []
    for key, (path, number, expected) in CHECKS.items():
        lines = sources.get(path, "").splitlines()
        observed = lines[number - 1] if len(lines) >= number else ""
        checks.append({
            "id": key, "file": path, "line": number,
            "passed": expected in observed.split("--", 1)[0],
            "evidence_grade": "source_text_only",
        })
    return {
        "repository": REPO,
        "commit": PIN,
        "passed": bool(checks) and all(x["passed"] for x in checks),
        "checks": checks,
        "lean_elaboration": False,
        "kernel_verification": False,
        "mathematical_validity": "not assessed",
    }


def fetch_pinned(path):
    if path not in {row[0] for row in CHECKS.values()}:
        raise ValueError("File not on RH source allowlist")
    url = f"https://raw.githubusercontent.com/{REPO}/{PIN}/{path}"
    with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=45) as response:
        raw = response.read(80_001)
    if len(raw) > 80_000:
        raise ValueError("File too large for this source check")
    return raw.decode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-pinned", action="store_true")
    args = parser.parse_args(argv)
    if not args.fetch_pinned:
        parser.error("Pass --fetch-pinned for the unauthenticated, immutable-commit source check")
    paths = {row[0] for row in CHECKS.values()}
    report = inspect({path: fetch_pinned(path) for path in sorted(paths)})
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
