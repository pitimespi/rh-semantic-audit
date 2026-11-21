"""Validate the exact RH analytic subgraph against immutable source lines.

The check confirms that a *named theorem call* occurs at the indicated Lean
source line. It does NOT establish a kernel dependency, correct mathematical
interpretation, or valid proof of the named result.
"""
import argparse
import json
import re
import urllib.request
from pathlib import Path

from semantic_graph.core import load, validate

GRAPH = Path("examples/rh_analytic_bridge.json")
REPOSITORY = "https://github.com/Deicyde/riemann-hypothesis"
EXPECTED_REV = "e50d09817ad81469f737e8f637561e6ccf86c670"

def source_line_checks(graph, sources):
    project = graph.get("project", {})
    if project.get("repository") != REPOSITORY or project.get("revision") != EXPECTED_REV:
        return [{"error": "Unrecognized repository/revision"}]
    errs = validate(graph)
    if errs:
        return [{"error": "Invalid semantic graph", "problems": errs}]
    by_id = {node["id"]: node for node in graph["nodes"]}
    results = []
    for edge in graph["edges"]:
        if edge["kind"] != "source_reference":
            continue
        ev = edge["evidence"]["source"]
        file = ev["path"]
        url = ev["url"]
        tail = url.rpartition("#L")
        if not tail[1] or not tail[2].isdigit():
            results.append({"edge": edge["id"], "passed": False, "problem": "Source line missing"})
            continue
        line = int(tail[2])
        text = sources.get(file, "").splitlines()
        symbol = by_id[edge["from"]]["symbol"].split(".")[-1]
        observed = text[line - 1] if 1 <= line <= len(text) else ""
        # Strip a trailing Lean line comment, then look for the cited constant.
        code = observed.split("--", 1)[0]
        pattern = r"(?<![\w])" + re.escape(symbol) + r"(?![\w])"
        found = re.search(pattern, code) is not None
        results.append({
            "edge": edge["id"],
            "symbol": symbol,
            "path": file,
            "line": line,
            "passed": found,
        })
    return results

def fetch_pinned_sources(graph):
    p = graph["project"]
    if p.get("repository") != REPOSITORY or p.get("revision") != EXPECTED_REV:
        raise ValueError("Refusing unrecognized RH graph origin")
    files = {e["evidence"]["source"]["path"]
             for e in graph["edges"] if e["kind"] == "source_reference"}
    files |= {n["source"]["path"] for n in graph["nodes"]}
    if len(files) > 12:
        raise ValueError("Unexpectedly many source files")
    for file in files:
        if not file.startswith("src/Development/AutomorphicArithmetic/") or ".." in file.split("/"):
            raise ValueError("Source file outside RH allowlist")
    result = {}
    for file in sorted(files):
        url = f"https://raw.githubusercontent.com/Deicyde/riemann-hypothesis/{EXPECTED_REV}/{file}"
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read(500_001)
        if len(data) > 500_000:
            raise ValueError("Source file exceeds 500 KB")
        result[file] = data.decode("utf-8")
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", default=str(GRAPH), help="Path to RH graph fixture at the pinned mirror revision")
    parser.add_argument("--fetch-pinned", action="store_true")
    args = parser.parse_args(argv)
    if not args.fetch_pinned:
        parser.error("Pass --fetch-pinned to run this source-text checker")
    graph = load(args.graph)
    results = source_line_checks(graph, fetch_pinned_sources(graph))
    print(json.dumps({
        "type": "source-line syntactic checks only; NOT Lean/kernel review",
        "commit": EXPECTED_REV,
        "edges_checked": len(results),
        "passed": all(r.get("passed", False) for r in results),
        "results": results,
    }, indent=2, ensure_ascii=False))
    return 0 if results and all(r.get("passed", False) for r in results) else 2

if __name__ == "__main__":
    raise SystemExit(main())
