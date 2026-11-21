"""CLI for versioned semantic proof graph prototypes (standard library only)."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from .core import import_candidates, load, render_markdown, render_mermaid, validate


def check_imports(graph, checkout):
    """Confirm only that a proposed theorem was imported; not that its proof uses it."""
    checkout = Path(checkout).resolve()
    actual = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                            check=True, capture_output=True, text=True).stdout.strip()
    pin = graph["project"]["revision"]
    if actual != pin:
        raise ValueError(f"checkout at {actual}, fixture requires {pin}")
    result = []
    by_id = {n["id"]: n for n in graph["nodes"]}
    for edge in graph["edges"]:
        if edge["kind"] != "import_candidate":
            continue
        source = edge["evidence"]["source"]["path"]
        file = (checkout / source).resolve()
        if checkout not in file.parents:
            raise ValueError("source escapes checkout")
        if not file.is_file():
            result.append({"edge": edge["id"], "file": source, "import_present": False, "reason": "file missing"})
            continue
        name = by_id[edge["from"]]["symbol"].replace(".", "_")
        module = "Theorems.Thm_" + name
        found = module in import_candidates(file.read_text(encoding="utf-8"))
        result.append({"edge": edge["id"], "file": source, "module": module,
                       "import_present": found})
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for cmd in ("validate", "mermaid", "report", "check-imports"):
        s = sub.add_parser(cmd)
        s.add_argument("graph", type=Path)
        if cmd == "report":
            s.add_argument("--target", default=None, help="Restrict to ancestors of this node")
        if cmd == "check-imports":
            s.add_argument("--checkout", required=True, type=Path,
                           help="An exact Git checkout at the graph's pinned revision")
    args = p.parse_args(argv)
    graph = load(args.graph)
    errs = validate(graph)
    if errs:
        print("\n".join(f"ERROR: {e}" for e in errs), file=sys.stderr)
        return 2
    if args.command == "validate":
        print(f"VALID {args.graph}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    elif args.command == "mermaid":
        print(render_mermaid(graph), end="")
    elif args.command == "report":
        print(render_markdown(graph, args.target))
    elif args.command == "check-imports":
        try:
            result = check_imports(graph, args.checkout)
        except (ValueError, OSError, subprocess.CalledProcessError) as ex:
            print("ERROR: " + str(ex), file=sys.stderr)
            return 2
        print(json.dumps(result, indent=2))
        if not all(x["import_present"] for x in result):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
