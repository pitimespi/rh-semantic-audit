"""Data contract and validation for reviewable, provider-neutral semantic proof graphs.

An edge with 'import_candidate' is never a verified proof dependency.
Explanations are annotations, NEVER Lean kernel certificates.
"""
import json
import re
from collections import deque
from pathlib import Path
from urllib.parse import quote

SCHEMA = "semantic-proof-graph/v1"
KINDS = {"source_reference", "import_candidate", "platform_decomposition", "kernel_dependency"}
REVIEWS = {"draft", "independent_review", "disputed"}
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.:_-]*$")


def load(path):
    """Load JSON and fail on duplicate JSON object keys."""
    def distinct(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f"duplicate JSON key: {k}")
            out[k] = v
        return out
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=distinct)


def _plain_source(source, project):
    if not isinstance(source, dict):
        return False
    path, url = source.get("path"), source.get("url")
    repo, rev = project.get("repository"), project.get("revision")
    if not all(isinstance(x, str) and x for x in (path, url, repo, rev)):
        return False
    if path.startswith("/") or ".." in path.split("/") or "://" in path:
        return False
    # Source URLs are pinned to commit, not mutable main branch.
    expected = repo.rstrip("/") + "/blob/" + rev + "/" + quote(path, safe="/")
    return url == expected or url.startswith(expected + "#L")


def validate(doc):
    """Return a list of actionable errors. No kernel or Lean claims are inferred."""
    errors = []
    if not isinstance(doc, dict):
        return ["document must be a JSON object"]
    if doc.get("schema_version") != SCHEMA:
        errors.append("schema_version must be " + SCHEMA)
    project = doc.get("project")
    if not isinstance(project, dict):
        return errors + ["project must be an object"]
    if not isinstance(project.get("id"), str) or not project["id"].strip():
        errors.append("project.id is required")
    if not isinstance(project.get("repository"), str) or not project["repository"].startswith("https://github.com/"):
        errors.append("project.repository must be a GitHub URL")
    if not isinstance(project.get("revision"), str) or not HEX40.fullmatch(project["revision"]):
        errors.append("project.revision must be a full 40-character commit SHA")
    nodes, edges = doc.get("nodes"), doc.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return errors + ["nodes and edges must be arrays"]
    ids = set()
    for idx, n in enumerate(nodes):
        label = f"nodes[{idx}]"
        if not isinstance(n, dict):
            errors.append(label + " must be object")
            continue
        nid = n.get("id")
        if not isinstance(nid, str) or not ID.fullmatch(nid):
            errors.append(label + ".id is invalid")
        elif nid in ids:
            errors.append(label + ".id duplicated: " + nid)
        else:
            ids.add(nid)
        for key in ("symbol", "title", "statement"):
            if not isinstance(n.get(key), str) or not n[key].strip():
                errors.append(f"{label}.{key} must be nonempty text")
        if not _plain_source(n.get("source"), project):
            errors.append(label + ".source needs path and pinned blob URL")
        proposal = n.get("proposal_record")
        if proposal is not None:
            if not isinstance(proposal, dict) or proposal.get("id_type") != "proposal_item" or proposal.get("id_is_a_theorem_id") is not False:
                errors.append(label + ".proposal_record must explicitly be a proposal_item, NOT theorem_id")
            elif any(not isinstance(proposal.get(k), str) or not proposal[k].strip()
                     for k in ("proposal_id", "proposal_item_id")) or "theorem_id" in proposal:
                errors.append(label + ".proposal_record missing IDs or conflates theorem_id")
        detail = n.get("theorem_record")
        if detail is not None:
            if not isinstance(detail, dict) or detail.get("provider") != "prove2me":
                errors.append(label + ".theorem_record provider invalid")
            elif not all(isinstance(detail.get(k), str) and detail[k].strip()
                         for k in ("theorem_id", "theorem_name", "formal_statement", "detail_snapshot_sha256", "endpoint")):
                errors.append(label + ".theorem_record needs theorem_id, name, statement, digest and endpoint")
            elif detail["theorem_name"] != n.get("symbol") or not HEX64.fullmatch(detail["detail_snapshot_sha256"]):
                errors.append(label + ".theorem_record name or digest mismatch")
            elif detail["endpoint"] != "https://prove2.me/api/v1/theorems/" + detail["theorem_id"]:
                errors.append(label + ".theorem_record must use exact Prove2me theorem endpoint")
        assumptions = n.get("assumptions")
        if not isinstance(assumptions, list):
            errors.append(label + ".assumptions must be array (can be empty)")
        else:
            for a in assumptions:
                if not isinstance(a, dict) or not all(isinstance(a.get(k), str) and a[k].strip() for k in ("name", "meaning")):
                    errors.append(label + ".assumptions entries need name and meaning")
    theorem_ids = [n.get("theorem_record", {}).get("theorem_id") for n in nodes if isinstance(n, dict) and isinstance(n.get("theorem_record"), dict)]
    if len(set(theorem_ids)) != len(theorem_ids):
        errors.append("duplicate authoritative theorem IDs attached to different nodes")
    edgeids = set()
    for idx, e in enumerate(edges):
        label = f"edges[{idx}]"
        if not isinstance(e, dict):
            errors.append(label + " must be object")
            continue
        eid = e.get("id")
        if not isinstance(eid, str) or not ID.fullmatch(eid):
            errors.append(label + ".id is invalid")
        elif eid in edgeids:
            errors.append(label + ".id duplicated: " + eid)
        else:
            edgeids.add(eid)
        for end in ("from", "to"):
            if e.get(end) not in ids:
                errors.append(label + f".{end} references unknown node")
        if e.get("from") == e.get("to"):
            errors.append(label + " is self-referential")
        if e.get("kind") not in KINDS:
            errors.append(label + ".kind must be one of " + ", ".join(sorted(KINDS)))
        evidence = e.get("evidence")
        if not isinstance(evidence, dict) or not _plain_source(evidence.get("source"), project):
            errors.append(label + ".evidence.source must link to pinned source")
        elif e.get("kind") == "kernel_dependency":
            if evidence.get("method") != "kernel_trace" or not isinstance(evidence.get("certificate"), str) or not evidence["certificate"].strip():
                errors.append(label + " kernel_dependency needs kernel_trace and certificate")
        elif e.get("kind") == "platform_decomposition":
            api = evidence.get("api")
            if evidence.get("method") != "platform_decomposition_api" or not isinstance(api, dict):
                errors.append(label + " platform_decomposition needs a recorded API snapshot")
            elif not all(isinstance(api.get(k), str) and api[k].strip()
                         for k in ("endpoint", "snapshot_sha256", "submission_id")):
                errors.append(label + " platform_decomposition needs endpoint, SHA-256 and submission ID")
            elif not HEX64.fullmatch(api["snapshot_sha256"]) or not api["endpoint"].startswith("https://prove2.me/api/v1/theorems/"):
                errors.append(label + " platform_decomposition snapshot provenance is invalid")
        elif evidence.get("method") not in ("textual_reference", "import_statement"):
            errors.append(label + " source-level evidence method required")
        semantic = e.get("semantic")
        if not isinstance(semantic, dict):
            errors.append(label + ".semantic annotation required")
            continue
        if not all(isinstance(semantic.get(k), str) and semantic[k].strip() for k in ("role", "explanation")):
            errors.append(label + ".semantic needs role and explanation")
        if semantic.get("review_status") not in REVIEWS:
            errors.append(label + ".semantic.review_status invalid")
        reviewers = semantic.get("reviewers")
        if not isinstance(reviewers, list) or any(not isinstance(x, str) or not x.strip() for x in reviewers):
            errors.append(label + ".semantic.reviewers must be list of nonempty names")
        elif semantic.get("review_status") == "independent_review" and len(set(reviewers)) < 2:
            errors.append(label + " independently reviewed semantics require two distinct reviewers")
    # Real theorem dependency DAG should be acyclic. Do not infer proof from cycles.
    indeg = {x: 0 for x in ids}
    out = {x: [] for x in ids}
    for e in edges:
        if isinstance(e, dict) and e.get("from") in ids and e.get("to") in ids:
            a,b=e["from"],e["to"]
            out[a].append(b)
            indeg[b]+=1
    q=deque(x for x,d in indeg.items() if d == 0)
    seen=0
    while q:
        u=q.popleft()
        seen+=1
        for v in out[u]:
            indeg[v]-=1
            if indeg[v]==0:
                q.append(v)
    if seen < len(ids):
        errors.append("dependency graph contains a directed cycle")
    return errors


def ancestors(doc, target):
    """All premise IDs with a directed path to target (not a proof validity claim)."""
    known={n["id"] for n in doc["nodes"]}
    if target not in known:
        raise KeyError(target)
    incoming={n:[] for n in known}
    for e in doc["edges"]:
        incoming[e["to"]].append(e["from"])
    result=set()
    todo=list(incoming[target])
    while todo:
        x=todo.pop()
        if x not in result:
            result.add(x)
            todo.extend(incoming[x])
    return sorted(result)


def render_mermaid(doc):
    """Stable Mermaid output from a validated graph; edges show evidence kind."""
    issues=validate(doc)
    if issues:
        raise ValueError("\n".join(issues))
    nodes=sorted(doc["nodes"],key=lambda x:x["id"])
    lines=["flowchart LR"]
    for n in nodes:
        label=n["title"].replace('"',"'").replace("\n"," ")
        lines.append(f'    {n["id"]}["{label}"]')
    for e in sorted(doc["edges"],key=lambda x:x["id"]):
        label={"source_reference":"source ref", "import_candidate":"import only", "platform_decomposition":"platform sketch", "kernel_dependency":"kernel trace"}[e["kind"]]
        lines.append(f'    {e["from"]} -->|{label}| {e["to"]}')
    lines.append("    %% Semantic text is independently reviewable annotation, not kernel evidence.")
    return "\n".join(lines)+"\n"


def render_markdown(doc, target=None):
    issues=validate(doc)
    if issues:
        raise ValueError("\n".join(issues))
    p=doc["project"]
    lines=[f'# {p["title"]}', "", f'Pinned source: [{p["repository"]}]({p["repository"]}/tree/{p["revision"]})', "",
           "> Source-level graph plus provisional semantic explanations; no independent proof-term verification is implied.", ""]
    by_id={n["id"]:n for n in doc["nodes"]}
    selected=set(by_id) if target is None else set(ancestors(doc,target))|{target}
    for n in sorted(doc["nodes"],key=lambda x:x["id"]):
        if n["id"] not in selected:
            continue
        lines.extend([f'## {n["title"]}', "",f'**Formal symbol:** `{n["symbol"]}`',
                      f'**Statement (human read-back):** {n["statement"]}',
                      f'**Source:** [Pinned definition]({n["source"]["url"]})', ""])
        proposal = n.get("proposal_record")
        if proposal:
            lines.append(f'**Prove2me proposal-item ID (not theorem ID):** \`{proposal["proposal_item_id"]}\`')
            if proposal.get("repository_reported_submission_status"):
                lines.append(f'**Locally reported status (not live verification):** {proposal["repository_reported_submission_status"]}')
            lines.append("")
        detail = n.get("theorem_record")
        if detail:
            lines.append(f'**Prove2me theorem ID (from cached API response):** \`{detail["theorem_id"]}\`')
            lines.append(f'**Reported platform status (snapshot only):** {detail.get("status_as_reported_by_api")}')
            lines.append("")
        for a in n["assumptions"]:
            lines.append(f'- Assumption **{a["name"]}**: {a["meaning"]}')
        if n["assumptions"]:
            lines.append("")
        for e in sorted(doc["edges"],key=lambda x:x["id"]):
            if e["to"]==n["id"] and e["from"] in selected:
                sem=e["semantic"]
                lines.extend([f'- **Input `{by_id[e["from"]]["symbol"]}`** ({e["kind"]}; semantic review: {sem["review_status"]}). '
                              f'{sem["role"]}: {sem["explanation"]} '
                              f'[Evidence]({e["evidence"]["source"]["url"]})'])
        lines.append("")
    return "\n".join(lines)


def import_candidates(source_text):
    """Read Lean import lines; returns strings ONLY, not theorem dependencies."""
    return [m.group(1) for ln in source_text.splitlines()
            if (m:=re.match(r'^import\s+(Theorems\.Thm_[A-Za-z0-9_]+)\s*$',ln))]
