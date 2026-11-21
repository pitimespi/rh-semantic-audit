"""CLI for the source-aware semantic proof graph project (Python stdlib only)."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .core import import_candidates, load, render_markdown, render_mermaid, validate
from .prove2me import (
    add_decompositions, bind_theorem_details, fetch_readonly, link_proposal,
)


def check_pin(graph, checkout):
    checkout = Path(checkout).resolve()
    actual = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    pin = graph["project"]["revision"]
    if actual != pin:
        raise ValueError(f"checkout at {actual}, fixture requires {pin}")
    return checkout


def check_imports(graph, checkout):
    """Confirm only that a theorem module was imported; NOT proof-term use."""
    checkout = check_pin(graph, checkout)
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


def write_json(path, obj):
    target = Path(path)
    if target.exists():
        raise ValueError(f"Refusing to overwrite existing file: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {target}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for cmd in ("validate", "mermaid", "report", "check-imports", "link-proposal", "bind-theorems", "merge-decompositions"):
        s = sub.add_parser(cmd)
        s.add_argument("graph", type=Path)
        if cmd == "report":
            s.add_argument("--target", default=None, help="Restrict to ancestors of this node")
        if cmd == "check-imports":
            s.add_argument("--checkout", required=True, type=Path)
        if cmd == "link-proposal":
            s.add_argument("--checkout", required=True, type=Path, help="Pinned Git checkout of the local proposal records")
            s.add_argument("--proposal", required=True, type=Path)
            s.add_argument("--submissions", type=Path)
            s.add_argument("--out", required=True, type=Path)
        if cmd == "bind-theorems":
            s.add_argument("--snapshot", required=True, type=Path, help="Cached GET theorem response or list of responses")
            s.add_argument("--out", required=True, type=Path)
        if cmd == "merge-decompositions":
            s.add_argument("--snapshot", required=True, type=Path, help="Cached GET /decompositions response")
            s.add_argument("--parent-id", required=True, help="Graph-local parent node ID already bound to actual theorem_id")
            s.add_argument("--out", required=True, type=Path)
    f = sub.add_parser("fetch-prove2me", help="One authenticated READ-ONLY GET; saves response locally, no credential persisted")
    f.add_argument("--theorem-id", required=True)
    f.add_argument("--kind", choices=("theorem", "decompositions"), required=True)
    f.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        if args.command == "fetch-prove2me":
            if args.out.exists():
                raise ValueError(f"Refusing to overwrite existing output: {args.out}")
            result = fetch_readonly(args.theorem_id, args.kind, os.environ.get("PROVE2ME_ACCESS_TOKEN", ""))
            write_json(args.out, result)
            return 0

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
            result = check_imports(graph, args.checkout)
            print(json.dumps(result, indent=2))
            if not all(x["import_present"] for x in result):
                return 1
        elif args.command == "link-proposal":
            checkout = check_pin(graph, args.checkout)
            proposal = args.proposal.resolve()
            if checkout not in proposal.parents:
                raise ValueError("proposal must be inside pinned source checkout")
            submission = args.submissions.resolve() if args.submissions else None
            if submission is not None and checkout not in submission.parents:
                raise ValueError("submissions snapshot must be inside pinned source checkout")
            out, summary = link_proposal(graph, load(proposal), load(submission) if submission else None)
            write_json(args.out, out)
            print(json.dumps(summary, indent=2))
        elif args.command == "bind-theorems":
            out, matched = bind_theorem_details(graph, load(args.snapshot))
            write_json(args.out, out)
            print(f"Bound {len(matched)} actual theorem IDs (from supplied API snapshot).")
        elif args.command == "merge-decompositions":
            out, summary = add_decompositions(graph, args.parent_id, load(args.snapshot))
            write_json(args.out, out)
            print(json.dumps(summary, indent=2))
        return 0
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as ex:
        print("ERROR: " + str(ex), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
