# Post the RH source-level research reference to Prove2me

**Status:** contribution **prepared**, not submitted by this repository or ChatGPT.

The [public Riemann Hypothesis mission](https://prove2.me/missions/The_Riemann_Hypothesis) is the intended destination. The platform explicitly supports posting `article` resources to missions via `POST /api/v1/missions/:id/resources`; see the [official Prove2me mission-resource API documentation](https://github.com/prove2me/prove2me_workspace/blob/main/references/missions.md#resources).

## Content

- [AUDIT-007 — Minkowski conditional-discharge review](../audit/AUDIT-007-MINKOWSKI-DISCHARGE.md)
- [Exact article-resource payload](../contributions/rh_minkowski_resource.json)

The audit finds that a potentially misleading conditional `MinkDiv → ExS` in the **actual RH proof branch** is supplied a named proof term at a downstream use. It is **not** a claim that RH is proved, an independently verified proof, a proof gap, or a missing hypothesis report. Its remaining issue is the nonvacuity of the definite-side and row-selection conditions.

This is an **article/resource contribution** rather than a Lean proof submission. It does not resolve the mission, change any theorem, contact anyone, or label the claimed proof flawed.

## Secure one-time local posting

A key previously pasted in a chat should be **revoked** and **replaced** first. Do not reuse it, commit it, store it in workflow configuration, paste it into an issue, or send it in a shell argument.

From your local `rh-semantic-audit` clone, see the exact publication description without using any credentials:

```bash
python3 -m semantic_graph.post_rh_resource
```

For the single authorized submission, obtain a new Prove2me API key. Set it invisibly in your shell:

```bash
read -rsp "New Prove2me API key: " PROVE2ME_API_KEY; echo
export PROVE2ME_API_KEY

python3 -m semantic_graph.post_rh_resource \
  --apply --confirm-mission-slug The_Riemann_Hypothesis

unset PROVE2ME_API_KEY
```

The code will:

1. Exchange the local API key for a short-lived token **in memory**.
2. Resolve the mission using **both** the exact name `The Riemann Hypothesis` and its exact target theorem name `riemann_hypothesis`.
3. List existing resources and reject an already published URL without posting again.
4. POST only the checked-in research article to the official mission-resources API with redirect blocking.
5. Report `published` only upon HTTP 201 and a matching resource URL. The response includes the resource ID.

No secret appears in the resource payload or posted URL. The script sends a single write request, and only in `--apply` mode. Tests mock the API and do not publish anything.

**Execution limitation in this ChatGPT conversation:** GitHub file access is connected, but a direct authenticated Prove2me POST is not. The user's previous permission to use an API key does not make the key available through a secure Prove2me connector. Accordingly, the article can be published **from the user's local machine**, not directly from this conversation. Do not claim the resource has been posted unless the API response reports success.

## Why not post a proof-gap insight?

The finding is a **discharged** conditional obligation, not an error. Prove2me's `proof_gap` or `missing_hypothesis` mission-comment tags would misrepresent it. A research resource is the correct supported format. If future work uncovers a genuine counterexample or a faithful formalization mismatch, it should be documented and reviewed as a separate finding.
