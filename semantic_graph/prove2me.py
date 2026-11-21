"""Read-only Prove2me integration.

Three boundaries:
1. GitHub mission proposal item IDs are NOT theorem IDs.
2. A platform decomposition is a server-recorded proof-sketch dependency,
   not a kernel-exported proof-term dependency.
3. Human explanations are provisional annotations, never proof certificates.

The network helper uses only GET endpoints at the documented Prove2me API
base and never persists credentials.
"""
import copy
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from uuid import UUID

from .core import validate

BASE = "https://prove2.me/api/v1"
UUID_PATTERN = re.compile(r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$")


def valid_uuid(value):
    return isinstance(value, str) and bool(UUID_PATTERN.fullmatch(value)) and bool(UUID(value))


def snapshot_hash(data):
    """SHA-256 of the canonical JSON representation, not of transport bytes."""
    b = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def link_proposal(graph, proposal, reported_submissions=None):
    """Attach local PROPOSAL-ITEM IDs to matching nodes, never theorem IDs.

    For missing mapped items, do not invent IDs. The submissions file is a
    repository-reported snapshot, *not* proof of the platform's current status.
    """
    if validate(graph):
        raise ValueError("input graph invalid: " + "; ".join(validate(graph)))
    if not isinstance(proposal, dict) or not valid_uuid(proposal.get("proposal_id")):
        raise ValueError("proposal needs a valid proposal_id UUID")
    items = proposal.get("items")
    if not isinstance(items, dict):
        raise ValueError("proposal.items must be an object")
    if any(not isinstance(k, str) or not valid_uuid(v) for k, v in items.items()):
        raise ValueError("proposal.items entries need symbol -> proposal item UUID")
    if reported_submissions is not None and not isinstance(reported_submissions, dict):
        raise ValueError("reported submissions must be an object")
    out = copy.deepcopy(graph)
    matched = []
    for n in out["nodes"]:
        symbol = n["symbol"]
        if symbol not in items:
            continue
        p = {"provider": "prove2me", "id_type": "proposal_item",
             "proposal_id": proposal["proposal_id"],
             "proposal_item_id": items[symbol],
             "id_is_a_theorem_id": False}
        if reported_submissions is not None and symbol in reported_submissions:
            status = reported_submissions[symbol]
            if not isinstance(status, str) or not status.strip():
                raise ValueError(f"invalid repository status for {symbol}")
            p["repository_reported_submission_status"] = status
        n["proposal_record"] = p
        matched.append(symbol)
    if validate(out):
        raise ValueError("output graph failed validation")
    return out, {"matched": matched,
                 "not_in_graph": sorted(set(items)-set(matched)),
                 "graph_nodes_without_proposal_item": sorted(n["symbol"] for n in out["nodes"] if n["symbol"] not in items)}


def bind_theorem_details(graph, payload):
    """Attach actual theorem IDs from explicit GET /theorems/:id responses.

    Names must match graph symbols EXACTLY. Missing/ambiguous details fail
    rather than being reconciled by a fuzzy name search.
    """
    if validate(graph):
        raise ValueError("input graph invalid")
    if isinstance(payload, dict) and "theorems" in payload:
        records = payload["theorems"]
    elif isinstance(payload, list):
        records = payload
    else:
        records = [payload]
    if not isinstance(records, list):
        raise ValueError("theorems must be an array")
    out = copy.deepcopy(graph)
    by_name = {n["symbol"]: n for n in out["nodes"]}
    bound = []
    seen = set()
    for detail in records:
        if not isinstance(detail, dict):
            raise ValueError("each theorem response must be an object")
        name = detail.get("theorem_name")
        tid = detail.get("theorem_id")
        if name not in by_name:
            raise ValueError(f"unknown theorem name in API response: {name!r}")
        if not valid_uuid(tid):
            raise ValueError(f"invalid theorem UUID for {name}")
        if name in seen:
            raise ValueError(f"duplicate theorem response: {name}")
        if any(x.get("theorem_record", {}).get("theorem_id") == tid and x["symbol"] != name for x in out["nodes"]):
            raise ValueError(f"theorem ID collision: {tid}")
        seen.add(name)
        n = by_name[name]
        statement = detail.get("formal_statement")
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError("API theorem record must provide formal_statement")
        n["theorem_record"] = {
            "provider": "prove2me",
            "theorem_id": tid,
            "theorem_name": name,
            "formal_statement": statement,
            "status_as_reported_by_api": detail.get("status"),
            "mathlib_rev_as_reported_by_api": detail.get("mathlib_rev"),
            "detail_snapshot_sha256": snapshot_hash(detail),
            "endpoint": f"{BASE}/theorems/{tid}",
            "meaning": "Unverified cached API response, distinct from a formal kernel certificate.",
        }
        bound.append(name)
    if validate(out):
        raise ValueError("output graph failed validation")
    return out, sorted(bound)


def add_decompositions(graph, parent_node_id, payload):
    """Import verified-shape API data for known theorem IDs, preserving original edges.

    Does not fetch other nodes or guess mappings for missing ones.
    Multiple sketches may conflict logically; they are alternatives, not a
    conjunction. Each edge records its sketch submission_id.
    """
    if validate(graph):
        raise ValueError("input graph invalid")
    out = copy.deepcopy(graph)
    by_id = {n["id"]: n for n in out["nodes"]}
    if parent_node_id not in by_id:
        raise KeyError(parent_node_id)
    parent = by_id[parent_node_id]
    parent_tid = parent.get("theorem_record", {}).get("theorem_id")
    if not valid_uuid(parent_tid):
        raise ValueError("parent requires a bound actual theorem_id (not proposal_item_id)")
    if not isinstance(payload, dict) or not isinstance(payload.get("decompositions"), list):
        raise ValueError("payload must contain a decompositions array")
    api_endpoint = f"{BASE}/theorems/{parent_tid}/decompositions"
    digest = snapshot_hash(payload)
    by_theorem_id = {n.get("theorem_record", {}).get("theorem_id"): n for n in out["nodes"] if n.get("theorem_record")}
    added, unresolved = [], []
    for row in payload["decompositions"]:
        if not isinstance(row, dict) or not valid_uuid(row.get("submission_id")) or not isinstance(row.get("children"), list):
            raise ValueError("decomposition needs submission_id UUID and children array")
        sid = row["submission_id"]
        for child in row["children"]:
            if not isinstance(child, dict):
                raise ValueError("child must be an object")
            tid = child.get("theorem_id")
            if tid is None:
                # Definition dependencies are intentionally not miscast as theorem nodes.
                if child.get("definition_id") is not None:
                    unresolved.append({"submission_id": sid, "definition_id": child["definition_id"], "reason": "definition_not_mapped"})
                    continue
                raise ValueError("child missing theorem_id or definition_id")
            if not valid_uuid(tid):
                raise ValueError("child theorem_id must be UUID")
            n = by_theorem_id.get(tid)
            if n is None:
                unresolved.append({"submission_id": sid, "theorem_id": tid, "reason": "theorem_not_mapped"})
                continue
            if child.get("theorem_name") != n["symbol"]:
                raise ValueError("child theorem_name does not match bound theorem")
            eid = f"p2m_{sid.replace('-', '')}_{n['id']}_{parent_node_id}"
            if any(e["id"] == eid for e in out["edges"]):
                continue
            e = {
                "id": eid,
                "from": n["id"], "to": parent_node_id,
                "kind": "platform_decomposition",
                "evidence": {
                    "method": "platform_decomposition_api",
                    "source": parent["source"],
                    "api": {"endpoint": api_endpoint, "snapshot_sha256": digest,
                            "submission_id": sid},
                },
                "semantic": {
                    "role": "Recorded Prove2me sketch child (mathematical role not yet reviewed)",
                    "explanation": f"The platform's cached decomposition response lists {n['symbol']} as a child of {parent['symbol']} in submission {sid}. This is not an independently extracted Lean proof-term dependency.",
                    "review_status": "draft", "reviewers": [],
                },
            }
            out["edges"].append(e)
            added.append(eid)
    problems = validate(out)
    if problems:
        raise ValueError("resulting graph invalid: " + "; ".join(problems))
    return out, {"added": added, "unresolved": unresolved, "snapshot_sha256": digest}


class _NeverRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward authentication headers to a redirect target."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _get_json(url, token):
    if not url.startswith(BASE + "/"):
        raise ValueError("Prove2me API URL must stay on the pinned HTTPS origin")
    if not isinstance(token, str) or not token:
        raise ValueError("Set PROVE2ME_ACCESS_TOKEN for read-only API access")
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
    }, method="GET")
    opener = urllib.request.build_opener(_NeverRedirect())
    try:
        with opener.open(req, timeout=30) as response:
            if response.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                raise ValueError("API response is not JSON")
            raw = response.read(8_000_001)
            if len(raw) > 8_000_000:
                raise ValueError("Prove2me response exceeds size limit")
            return json.loads(raw)
    except urllib.error.HTTPError as ex:
        raise RuntimeError(f"Prove2me returned HTTP {ex.code} (redirects are disabled)") from None


def fetch_readonly(theorem_id, kind, token):
    """Fetch exactly one theorem or its decomposition; HTTP GET only."""
    if not valid_uuid(theorem_id):
        raise ValueError("theorem_id must be a UUID")
    if kind not in ("theorem", "decompositions"):
        raise ValueError("unsupported read endpoint")
    path = f"/theorems/{theorem_id}"
    if kind == "decompositions":
        path += "/decompositions"
    return _get_json(BASE + path, token)


def lookup_theorem_exact(theorem_name, token):
    """Search by exact Lean name, then fetch full theorem details.

    The search itself can match multiple names. Only an unambiguous exact
    match is accepted; no fuzzy correspondence is ever used as evidence.
    """
    if not isinstance(theorem_name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", theorem_name):
        raise ValueError("theorem_name must be a Lean-style qualified identifier")
    if len(theorem_name) > 160:
        raise ValueError("theorem_name is too long")
    url = BASE + "/theorems?" + urllib.parse.urlencode({
        "q": theorem_name, "view": "compact",
    })
    response = _get_json(url, token)
    candidates = response.get("theorems")
    if not isinstance(candidates, list):
        raise ValueError("theorem search result lacks a theorem array")
    matches = [x for x in candidates if isinstance(x, dict) and x.get("theorem_name") == theorem_name]
    if len(matches) != 1 or not valid_uuid(matches[0].get("theorem_id")):
        raise ValueError(f"Need exactly one real theorem ID for {theorem_name}, found {len(matches)}")
    detail = fetch_readonly(matches[0]["theorem_id"], "theorem", token)
    if not isinstance(detail, dict) or detail.get("theorem_name") != theorem_name:
        raise ValueError("theorem detail disagrees with search name")
    if detail.get("theorem_id") != matches[0]["theorem_id"]:
        raise ValueError("theorem detail ID disagrees with search")
    return detail
