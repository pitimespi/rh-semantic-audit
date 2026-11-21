# Prove2me integration — actual IDs, source provenance, and read-only APIs

**Prototype v0.6, 2026-11-20.** This adapter makes no account changes and does not submit theorem proofs, mission edits, comments, or reviews. It is not connected to any Prove2me account in this repository.

The official [Prove2me skill's API documentation](https://github.com/prove2me/prove2me_workspace/blob/main/SKILL.md) describes the read-only endpoints used here:

- \`GET https://prove2.me/api/v1/theorems?q=...&view=compact\` — discover candidate theorem IDs.
- \`GET https://prove2.me/api/v1/theorems/:theorem_id\` — fetch the canonical theorem record.
- \`GET https://prove2.me/api/v1/theorems/:theorem_id/decompositions\` — fetch a theorem's **platform-recorded proof sketch/reduction** children.

**Auth:** The documented Prove2me API key can be exchanged at `POST https://prove2.me/api/v1/agent/refresh` for a short-lived Bearer access token. The adapter reads `PROVE2ME_API_KEY` or `PROVE2ME_ACCESS_TOKEN` only from the local process environment. It performs **GET requests for theorem data and a single POST exclusively for authentication**. Redirects are disabled; credentials are never written to files or logs. Never commit or paste credentials into an issue, log or chat.

## Set up a key without exposing it in GitHub or chat

1. On your local computer, log in to [Prove2me](https://prove2.me) and use the account menu → **API key**, following the [official setup guide](https://github.com/prove2me/prove2me_workspace/blob/main/references/setup.md).
2. From the root of a local \`rh-semantic-audit\` clone, run the following **in your shell**. This prompts invisibly rather than putting a key into a command-line argument or shell history:

   \`\`\`bash
   read -rsp "Prove2me API key: " PROVE2ME_API_KEY; echo
   export PROVE2ME_API_KEY
   python3 -m semantic_graph.cli lookup-prove2me \
     --theorem-name BitcoinSupply.supply_bound \
     --out outputs/theorem-supply-bound.json
   unset PROVE2ME_API_KEY
   \`\`\`

The adapter exchanges the key for an access token **in memory**, sends the access token only to the documented Prove2me theorem endpoints, and writes the resulting JSON theorem snapshot to the gitignored local \`outputs/\` directory. It does **not** store the key or token. Source records may include details from private missions; do not commit the output without checking its visibility.

If you already have a short-lived access token, you may supply \`PROVE2ME_ACCESS_TOKEN\` instead. It takes precedence over \`PROVE2ME_API_KEY\`. The key is intentionally not available to the GitHub Actions workflow or other public repository automation.

**This chat cannot directly read the key from your Prove2me account.** Authorization to use it is distinct from having it available in a runtime. Live retrieval has not been run here.

## Why three distinct IDs matter

| Data source | Field | Meaning | Safe conclusion |
|---|---|---|---|
| \`missions/submissions/supply_proposal.json\` in your pinned GitHub source | \`proposal_id\` | An existing mission proposal ID | Records a local proposal |
| The same file's \`items\` mapping | \`proposal_item_id\` | An ID for a draft/proposal item | **Not necessarily the published theorem ID** |
| \`GET /theorems/:theorem_id\` | \`theorem_id\` | Canonical platform theorem ID at API fetch time | May be used to address theorem/detail/decomposition endpoints |

A local \`ACCEPTED\` entry in \`supply_submissions.json\` is a **repository-reported status snapshot**, not a fresh API status or separate kernel check. This adapter never silently converts proposal items into theorem IDs.

## Current verified-from-GitHub example

The following three actual identifiers were read from the pinned \`pitimespi/prove2me\` commit \`64f338540bb1d4264d4f101d5dd656e290fa0afb\`:

| Theorem | Proposal item ID | Repository-reported submission status |
|---|---|---|
| \`BitcoinSupply.block_supply\` | \`8575bdcf-1596-4f22-bfaf-0c725ac7eaf4\` | ACCEPTED |
| \`BitcoinSupply.supply_bound\` | \`faa28708-d43f-446f-b6fc-16789c6befd2\` | ACCEPTED |
| \`BitcoinSupply.supply_lt_maxMoney\` | \`2d6e1f7f-9cfe-44f0-b1ea-6dc81b81a082\` | ACCEPTED |

They are included in [\`examples/bitcoin_supply_proposal_linked.json\`](../examples/bitcoin_supply_proposal_linked.json).

## Step 1: reproduce from the pinned GitHub data (no Prove2me token)

From this repository's root:

\`\`\`sh
git clone https://github.com/pitimespi/prove2me.git
git -C prove2me checkout 64f338540bb1d4264d4f101d5dd656e290fa0afb

python3 -m semantic_graph.cli link-proposal \
  examples/bitcoin_supply.json \
  --checkout prove2me \
  --proposal prove2me/missions/submissions/supply_proposal.json \
  --submissions prove2me/missions/submissions/supply_submissions.json \
  --out outputs/bitcoin-supply-local-proposal.json

python3 -m semantic_graph.cli validate outputs/bitcoin-supply-local-proposal.json
python3 -m semantic_graph.cli report outputs/bitcoin-supply-local-proposal.json
\`\`\`

The output contains proposal IDs and locally reported statuses only. The source checkout must be at the exact pinned revision; the CLI rejects a mismatched checkout. The output directory is gitignored.

## Step 2: optionally bind actual theorem IDs (authenticated read-only)

Use the local API-key prompt above (or an already obtained short-lived API access token) and follow the [official setup instructions](https://github.com/prove2me/prove2me_workspace/blob/main/references/setup.md). Do **not** commit your token or publish theorem responses from a private mission.

In your own shell, set `PROVE2ME_API_KEY` or `PROVE2ME_ACCESS_TOKEN`. The CLI does not save or print either credential.

To find a theorem ID and retrieve full details by exact name:

\`\`\`sh
python3 -m semantic_graph.cli lookup-prove2me \
  --theorem-name BitcoinSupply.supply_bound \
  --out outputs/theorem-supply-bound.json
\`\`\`

The adapter first searches, then requires a **unique exact name** before fetching full details. It rejects ambiguous matches, mismatched IDs, and malformed responses. Only the API-returned \`theorem_id\` can be treated as a theorem ID.

To link the theorem to the locally sourced graph:

\`\`\`sh
python3 -m semantic_graph.cli bind-theorems \
  outputs/bitcoin-supply-local-proposal.json \
  --snapshot outputs/theorem-supply-bound.json \
  --out outputs/supply-with-theorem-id.json
\`\`\`

Repeat lookup and binding (against the most recently generated graph) for any other theorem needed to build an edge. Keep API responses in a private local \`outputs/\` directory unless you have independently confirmed they contain only public data.

## Step 3: optionally import authoritative *platform decomposition records*

With a real theorem ID from Step 2, read its sketch decomposition:

\`\`\`sh
python3 -m semantic_graph.cli fetch-prove2me \
  --theorem-id YOUR_REAL_THEOREM_UUID \
  --kind decompositions \
  --out outputs/supply-decompositions.json
\`\`\`

After binding each relevant child theorem's ID, merge the cached decomposition:

\`\`\`sh
python3 -m semantic_graph.cli merge-decompositions \
  outputs/supply-with-all-needed-theorem-ids.json \
  --parent-id supply_bound \
  --snapshot outputs/supply-decompositions.json \
  --out outputs/supply-with-platform-decomposition.json
\`\`\`

The adapter imports only named child theorems with matching, already-bound IDs; unrecognized theorems and definition children are separately reported as \`unresolved\`. It **retains** previously recorded source/import edges so the evidence progression remains visible.

A \`platform_decomposition\` edge means only that the *cached Prove2me API response* listed the child in a particular proof-sketch submission. It does **not** establish that the parent has been proved without assumptions, that the child is still active, or that an independently exported Lean kernel proof term contains that child.

Each such edge carries the exact submission ID, a cryptographic SHA-256 digest of the canonical JSON response, and the API endpoint for repeat verification. \`kernel_dependency\` remains a separate, stronger category requiring a genuine kernel-trace certificate.

## Security and limitations

1. No API credentials are present in source or fixtures. All authentication is optional and read-only.
2. HTTP redirect-following is disabled for authenticated requests; URLs are built only on the official HTTPS base.
3. A recorded platform response may be stale. The graph stores the snapshot digest but does not assert current status.
4. Multiple decompositions of the same theorem are **alternative sketches**, not a single conjunction; each edge carries its submission ID.
5. The engine remains a research prototype, not an installed Prove2me extension. No contact with Prove2me maintainers or the RH verification community has occurred.
6. The graph's semantic explanations are draft, not independently reviewed. Accepting a proof-sketch edge does not validate its mathematical prose.

## Development

\`\`\`sh
python3 -m unittest discover -s tests -v
python3 -m semantic_graph.cli validate examples/bitcoin_supply_proposal_linked.json
\`\`\`

Unit tests use synthetic API payloads and the locally pinned proposal identifiers. No tests make live Prove2me requests.
