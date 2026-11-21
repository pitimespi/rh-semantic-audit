"""One-time RH research resource post to Prove2me.

Default mode is an unauthenticated, local preview. Publishing uses the
documented Prove2me mission-resources API. Requires a newly issued key in
PROVE2ME_API_KEY (or PROVE2ME_ACCESS_TOKEN) and --apply with exact
mission-name confirmation. No key is stored, logged or embedded in URLs.

Not a proof submission. The linked report is labeled source-text evidence.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .prove2me import BASE, _NeverRedirect, _get_json, access_token_from_environment, valid_uuid

MISSION_NAME = "The Riemann Hypothesis"
THEOREM_NAME = "riemann_hypothesis"
MISSION_SLUG = "The_Riemann_Hypothesis"
RESOURCE_FILE = Path("contributions/rh_minkowski_resource.json")
CANONICAL_URL = (
    "https://github.com/pitimespi/rh-semantic-audit/blob/main/"
    "audit/AUDIT-007-MINKOWSKI-DISCHARGE.md"
)
ALLOWED_TYPE = "article"


def load_resource(path=RESOURCE_FILE):
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"title", "url", "type", "description"}:
        raise ValueError("Resource must contain exactly title/url/type/description")
    if not 1 <= len(raw["title"]) <= 200 or raw["url"] != CANONICAL_URL:
        raise ValueError("Unexpected RH resource title or URL")
    if raw["type"] != ALLOWED_TYPE:
        raise ValueError("Only an article reference is allowed")
    if not isinstance(raw["description"], str) or not 1 <= len(raw["description"]) <= 4000:
        raise ValueError("Resource description invalid")
    return raw


def get_exact_rh_mission(token):
    """Never use fuzzy search results or an unverified destination mission."""
    params = urllib.parse.urlencode({"q": MISSION_NAME, "limit": 100, "offset": 0})
    result = _get_json(BASE + "/missions?" + params, token)
    rows = result.get("missions") if isinstance(result, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Prove2me mission search returned unexpected JSON")
    matches = [
        r for r in rows
        if isinstance(r, dict)
        and r.get("name") == MISSION_NAME
        and isinstance(r.get("main_theorem"), dict)
        and r["main_theorem"].get("theorem_name") == THEOREM_NAME
        and r.get("visibility", "public") == "public"
        and valid_uuid(r.get("id"))
    ]
    if len(matches) != 1:
        raise ValueError(f"Need exactly one matching public RH mission, found {len(matches)}")
    return matches[0]


def read_existing_resources(mission_id, token, cap=1000):
    if not valid_uuid(mission_id):
        raise ValueError("Mission UUID invalid")
    all_rows = []
    for offset in range(0, cap, 100):
        params = urllib.parse.urlencode({"sort": "newest", "limit": 100, "offset": offset})
        result = _get_json(BASE + f"/missions/{mission_id}/resources?" + params, token)
        rows = result.get("resources") if isinstance(result, dict) else None
        page = result.get("pagination") if isinstance(result, dict) else None
        if not isinstance(rows, list) or not isinstance(page, dict):
            raise ValueError("Unexpected Prove2me resource-list JSON")
        all_rows.extend(rows)
        count = page.get("total")
        if isinstance(count, int) and offset + len(rows) >= count:
            return all_rows
        if not rows:
            return all_rows
    raise ValueError("Resource list longer than cap; refusing to post before duplicate scan")


def post_resource(mission_id, token, resource):
    if not valid_uuid(mission_id):
        raise ValueError("Invalid mission UUID")
    if resource != load_resource():
        raise ValueError("Refusing to publish a modified/unknown resource payload")
    body = json.dumps(resource, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        BASE + f"/missions/{mission_id}/resources",
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    opener = urllib.request.build_opener(_NeverRedirect())
    try:
        with opener.open(request, timeout=30) as response:
            status = response.status
            raw = response.read(100_001)
            if len(raw) > 100_000:
                raise ValueError("Unexpectedly large Prove2me response")
            if response.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                raise ValueError("Unexpected media type for posting response")
            data = json.loads(raw)
    except urllib.error.HTTPError as ex:
        if ex.code == 409:
            raise RuntimeError("Resource already exists on Prove2me (HTTP 409); do not repost") from None
        raise RuntimeError(f"Prove2me resource publication returned HTTP {ex.code}") from None
    if status != 201:
        raise RuntimeError(f"Prove2me returned unexpected HTTP {status}; check before retrying")
    obj = data.get("resource") if isinstance(data, dict) and isinstance(data.get("resource"), dict) else data
    if not isinstance(obj, dict) or obj.get("url") != resource["url"]:
        raise RuntimeError("Publication response shape unexpected; verify on platform before retrying")
    return obj


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-file", type=Path, default=RESOURCE_FILE)
    parser.add_argument("--apply", action="store_true", help="POST one resource to Prove2me")
    parser.add_argument("--confirm-mission-slug",
                        help="To publish, must equal The_Riemann_Hypothesis")
    args = parser.parse_args(argv)
    try:
        resource = load_resource(args.resource_file)
        canonical = json.dumps(resource, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        print(json.dumps({
            "destination": f"https://prove2.me/missions/{MISSION_SLUG}",
            "title": resource["title"],
            "url": resource["url"],
            "type": resource["type"],
            "description": resource["description"],
            "payload_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "status": "ready_to_publish" if not args.apply else "checking_destination",
        }, indent=2, ensure_ascii=False))
        if not args.apply:
            print("PREVIEW ONLY — no Prove2me API call or publication.")
            return 0
        if args.confirm_mission_slug != MISSION_SLUG:
            raise ValueError("Publishing requires --confirm-mission-slug The_Riemann_Hypothesis")
        if args.resource_file != RESOURCE_FILE:
            raise ValueError("Publishing requires the checked-in canonical RH resource file")
        token = access_token_from_environment()
        mission = get_exact_rh_mission(token)
        duplicate = next((r for r in read_existing_resources(mission["id"], token)
                          if isinstance(r, dict) and r.get("url") == CANONICAL_URL), None)
        if duplicate is not None:
            print(json.dumps({"status": "already_exists", "mission_id": mission["id"],
                              "resource_id": duplicate.get("id")}, indent=2))
            return 0
        published = post_resource(mission["id"], token, resource)
        print(json.dumps({"status": "published", "mission_id": mission["id"],
                          "resource_id": published.get("id"), "url": published["url"]}, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError, TypeError, json.JSONDecodeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
