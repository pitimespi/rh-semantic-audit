"""Safe, opt-in publisher for Prove2me proof explanations.

Only modifies the natural-language explanation on an ACCEPTED submission
owned by the account. No proofs, theorems, discussions, or mission metadata
are changed. Dry run is the default; --apply and exact submission ID confirmation
are required to write.

Live requests must be run locally, with credentials in environment variables.
Never place API keys in command-line arguments, source, log output, or GitHub.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .prove2me import (
    BASE, _NeverRedirect, _get_json, access_token_from_environment,
    lookup_theorem_exact, valid_uuid,
)

ALLOWED = {"ACCEPTED", "SKETCH_ACCEPTED"}


def owner_submissions(token, max_pages=40):
    """List the authenticated account's submissions, not arbitrary users'."""
    found = []
    for page in range(1, max_pages + 1):
        data = _get_json(BASE + f"/submissions?page={page}", token)
        if not isinstance(data, dict) or not isinstance(data.get("submissions"), list):
            raise ValueError("Prove2me own-submissions response missing submissions")
        found.extend(data["submissions"])
        total = data.get("total")
        if isinstance(total, int) and total >= 0:
            if len(found) >= total:
                return found
        elif len(data["submissions"]) < 100:
            return found
        if not data["submissions"]:
            return found
    raise ValueError("Submission listing exceeds configured page cap; narrow the search")


def resolve_owned_target(name, token, submission_id=None):
    """Resolve exact theorem name and exactly one owned, accepted submission."""
    details = lookup_theorem_exact(name, token)
    theorem_id = details.get("theorem_id")
    if not valid_uuid(theorem_id):
        raise ValueError("Theorem lookup returned no authoritative theorem_id")
    own = [
        s for s in owner_submissions(token)
        if isinstance(s, dict)
        and s.get("theorem_id") == theorem_id
        and s.get("status") in ALLOWED
    ]
    if submission_id:
        if not valid_uuid(submission_id):
            raise ValueError("submission_id must be a valid UUID")
        own = [s for s in own if (s.get("id") or s.get("submission_id")) == submission_id]
    if len(own) != 1:
        raise ValueError(
            f"Expected exactly one owned accepted submission for {name}; found {len(own)}. "
            "Use --submission-id if you have more than one."
        )
    target = own[0]
    sid = target.get("id") or target.get("submission_id")
    if not valid_uuid(sid):
        raise ValueError("Owned submission record has no valid ID")
    # Freshly fetch published submission explanation and its status.
    params = urllib.parse.urlencode({"status": "ACCEPTED,SKETCH_ACCEPTED", "limit": "200"})
    data = _get_json(BASE + f"/theorems/{theorem_id}/submissions?{params}", token)
    if not isinstance(data, dict) or not isinstance(data.get("submissions"), list):
        raise ValueError("Theorem submissions response is invalid")
    fresh = [r for r in data["submissions"] if (r.get("id") or r.get("submission_id")) == sid]
    if len(fresh) != 1:
        raise ValueError(
            "Owned submission not present in current accepted submissions response; "
            "refusing to change an unverified target"
        )
    r = fresh[0]
    if r.get("theorem_id") != theorem_id or r.get("status") not in ALLOWED:
        raise ValueError("Current submission status or theorem ID mismatch")
    existing = r.get("explanation") or ""
    if not isinstance(existing, str):
        raise ValueError("Existing explanation is not text")
    return details, sid, existing


def proposed_explanation(file):
    path = Path(file)
    content = path.read_text(encoding="utf-8").strip()
    if not content or len(content) > 50_000:
        raise ValueError("Explanation must be nonempty and at most 50,000 characters")
    return content


def preview(theorem, sid, old, new):
    """A review summary; never prints credentials or private proof content."""
    return {
        "theorem_name": theorem["theorem_name"],
        "theorem_id": theorem["theorem_id"],
        "submission_id": sid,
        "published_status": theorem.get("status"),
        "existing_explanation_length": len(old),
        "existing_explanation_sha256": hashlib.sha256(old.encode()).hexdigest(),
        "new_explanation_length": len(new),
        "new_explanation_sha256": hashlib.sha256(new.encode()).hexdigest(),
        "unchanged": new == old,
        "action": "EDIT ONLY YOUR OWN ACCEPTED SUBMISSION EXPLANATION",
    }


def patch_explanation(submission_id, content, token):
    """Use PATCH only against the documented creator-owned explanation route."""
    if not valid_uuid(submission_id):
        raise ValueError("Invalid submission_id")
    data = json.dumps({"explanation": content}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        BASE + "/submissions/" + submission_id,
        data=data,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="PATCH",
    )
    opener = urllib.request.build_opener(_NeverRedirect())
    try:
        with opener.open(request, timeout=30) as response:
            if response.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                raise ValueError("Unexpected response media type")
            raw = response.read(100_001)
            if len(raw) > 100_000:
                raise ValueError("Unexpectedly large response")
            return json.loads(raw)
    except urllib.error.HTTPError as ex:
        raise RuntimeError(f"Prove2me explanation update returned HTTP {ex.code}") from None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--theorem-name", required=True, help="Exact Lean theorem name")
    p.add_argument("--explanation-file", required=True, type=Path, help="Reviewed Markdown explanation")
    p.add_argument("--submission-id", help="Disambiguate multiple accepted submissions")
    p.add_argument("--replace-existing", action="store_true", help="Explicitly allow replacing a nonempty explanation")
    p.add_argument("--apply", action="store_true", help="Publish explanation instead of previewing")
    p.add_argument("--confirm-submission-id", help="Required with --apply; must match resolved owned submission")
    args = p.parse_args(argv)
    try:
        content = proposed_explanation(args.explanation_file)
        token = access_token_from_environment()
        theorem, sid, current = resolve_owned_target(args.theorem_name, token, args.submission_id)
        print(json.dumps(preview(theorem, sid, current, content), indent=2))
        if content == current:
            print("No change needed.")
            return 0
        if current and not args.replace_existing:
            raise ValueError("Existing explanation is nonempty; review it before using --replace-existing")
        if not args.apply:
            print("PREVIEW ONLY: Nothing was submitted to Prove2me.")
            print("To submit, rerun with --apply --confirm-submission-id " + sid)
            return 0
        if args.confirm_submission_id != sid:
            raise ValueError("Refusing PATCH without exact --confirm-submission-id matching the owned submission")
        result = patch_explanation(sid, content, token)
        # Prove2me PATCH returns updated submission. Check rather than guessing.
        if not isinstance(result, dict):
            raise ValueError("PATCH returned unexpected shape; verify state before retrying")
        print("PATCH response received; verify the explanation on the Prove2me theorem page.")
        return 0
    except (ValueError, OSError, RuntimeError) as ex:
        print("ERROR: " + str(ex), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
