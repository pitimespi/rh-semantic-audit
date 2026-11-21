# Semantic proof graph — design, evidence, and usage

**Prototype version:** `semantic-proof-graph/v1` (2026-11-20). Code is in `semantic_graph/`; data in `examples/`. Python standard library only.

## Purpose

Support interpretation of formally stated theorems **without conflating** independently audited mathematics, source-text inspection, theorem imports, and kernel-certified dependencies.

Nodes are theorem statements (selected, human-readable, sourced). Edges are separately recorded, evidence-backed relationships from **premise → conclusion**; `semantic` annotations explain why the edge might matter. These explanations are interpretive claims, **not proof certificates**.

This builds on [Prove2me's source/read-back methodology](https://github.com/pitimespi/prove2me/blob/main/REVIEW.md) and is designed to remain external to the trusted Lean kernel.

## JSON contract

```json
{
  "schema_version": "semantic-proof-graph/v1",
  "project": {
    "id": "example",
    "title": "Example graph",
    "repository": "https://github.com/owner/repo",
    "revision": "0123456789abcdef0123456789abcdef01234567"
  },
  "nodes": [
    {
      "id": "A",
      "symbol": "Example.theoremA",
      "title": "Informal title",
      "statement": "Careful human read-back, without inventing assumptions.",
      "source": {
        "path": "Theorems/Example.lean",
        "url": "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/Theorems/Example.lean"
      },
      "assumptions": [{"name": "h", "meaning": "Mathematical hypothesis."}]
    }
  ],
  "edges": []
}
```

Four evidence classes are supported:

| Relationship | What it establishes | What it does not establish |
|---|---|---|
| `import_candidate` | An imported theorem module is visible in a proof source | That its theorem occurs in the final elaborated proof |
| `source_reference` | A named theorem is directly referenced by text | The complete kernel proof-term dependency graph |
| `platform_decomposition` | A cached Prove2me API response explicitly records a child under a particular proof-sketch submission | That an independent Lean kernel trace confirmed the edge, or that the child is currently active |
| `kernel_dependency` | An external kernel/compiled-proof dependency record is attached | The semantic annotation's mathematical interpretation |

**Policy:** `kernel_dependency` is rejected unless evidence declares `method: kernel_trace` and a non-empty `certificate` reference. No supplied example claims this class. Platform sketch edges require the API endpoint, exact submission ID, and SHA-256 of the canonical cached JSON response. See [the Prove2me integration guide](PROVE2ME-INTEGRATION.md).

Each edge also contains:

- `evidence.method`: `import_statement` or `textual_reference` for source-only edges.
- `evidence.source`: a specific pinned source file.
- `semantic.role` and `semantic.explanation`: human prose explaining the mathematical relation.
- `semantic.review_status`: `draft`, `independent_review`, or `disputed`.
- `semantic.reviewers`: identifiers for independent readers. A transition to `independent_review` requires at least two distinct reviewers.

The validator detects missing fields, duplicate IDs, non-pinned source URLs, dangling edges, cycles, unsupported evidence claims, and falsely claimed independent reviews. It **does not** test the truth of an explanation or verify that a cited source actually contains the theorem.

## Interactive graph browser

Use the [offline browser viewer](VIEWER.md) to inspect theorem nodes, source links, source-reference vs import-candidate edges, mathematical explanations, and pending review decisions. It does not execute Lean or call Prove2me APIs.

## Commands

```sh
python3 -m semantic_graph.cli validate examples/bitcoin_supply.json
python3 -m semantic_graph.cli mermaid examples/bitcoin_supply.json > bitcoin.mmd
python3 -m semantic_graph.cli validate examples/bitcoin_supply_proposal_linked.json
python3 -m semantic_graph.cli report examples/rh_critical_path.json --target headline > rh-review.md
python3 -m unittest discover -s tests -v
```

To confirm that the Bitcoin candidate edges correspond to imports in your exact pinned local checkout:

```sh
git clone https://github.com/pitimespi/prove2me.git
git -C prove2me checkout 64f338540bb1d4264d4f101d5dd656e290fa0afb
python3 -m semantic_graph.cli check-imports examples/bitcoin_supply.json --checkout prove2me
```

**This checks imports only. For source_reference edges citing explicit line numbers, run `python3 -m semantic_graph.cli check-references examples/bitcoin_supply_proposal_linked.json --checkout prove2me` to check source text. GitHub CI performs both checks at the pinned repository revision.** It explicitly refuses a checkout at a different revision and does not run Lean. No files in the checked-out project are modified.

The RH example is a curated source-reference chain, not an export of the original unlicensed source and not a new finding about the complete dependency graph. See [Keith Adler's earlier proof map](https://github.com/keithadler/rh-trim/blob/main/docs/PROOF-MAP.md).

## Why Bitcoin first

The existing [Prove2me Bitcoin supply mission](https://github.com/pitimespi/prove2me) has a high-level correctness story: subsidy schedule bound → reachable-chain supply bound → `MAX_MONEY` constraint. Its theorem statements have explicit reachability hypotheses, and its local `Solutions/Sol_*.lean` modules import earlier theorem stubs. This is a practical *candidate* semantic chain.

An appropriate first human audit would take `BitcoinSupply.supply_lt_maxMoney` and independently confirm every displayed statement, hypothesis, dependency, and arithmetic step against the actual source and the published platform's statements. Then attach reviewers to each explanatory edge.

## Future platform integration

A Prove2me platform integration could expose independent semantic edge annotations attached to existing theorem IDs and dependency edges. The platform remains the authority for formally accepted theorem statements and actual dependency identities. This project should **not** silently create platform proofs or call undocumented APIs.

First integration milestone: a read-only adapter that fetches versioned theorem IDs, statements, and published dependency edges through documented API contracts, then attaches reviewed annotations as separate provenance objects.

## Restrictions

- No secret keys, service calls, model-provider credentials, or external database required.
- No redistribution of unlicensed third-party Lean source.
- Source paths and commit pins must be checked before comparing a fixture to a local checkout.
- No community engagement or upstream submissions without owner authorization.
- The tool is a research prototype and does not decide whether the Riemann Hypothesis is true.
