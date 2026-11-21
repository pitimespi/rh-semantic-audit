# RH Semantic Audit

**Status: early research prototype, v0.5 (2026-11-20). Not an independent verification of the Riemann Hypothesis.**

A source-linked, human-oriented review of selected declarations in the purported Lean 4 proof of the Riemann Hypothesis announced by Levent Alpöge on November 20, 2026. It applies review methods developed in [Prove2me](https://github.com/pitimespi/prove2me): exact version pinning, independent read-backs, explicit hypothesis inventories, risk-ranked review, and provenance-aware reporting.

This is **not** a new proof, a proof validity determination, an original discovery of the top-level theorem chain, or a complete Lean dependency analysis. Independent kernel replay and statement checking are being undertaken by other researchers; see the references below. Our intended contribution is **explaining the mathematical content and interfaces inside a large formal proof**.

## Interactive viewer and source-grounded semantic proof (v0.5)

- **[Interactive graph viewer](viewer/index.html)**: explore either pinned example with clickable theorem nodes, assumption inventory, evidence grades, source links, and individual semantic explanations. Run \`python3 -m http.server 8000\` from the repository root and visit \`http://localhost:8000/viewer/\`, or open local JSON in the viewer. See [viewer documentation](docs/VIEWER.md).
- **[BITCOIN-001: UTXO supply ceiling](audit/BITCOIN-001-SUPPLY.md)**: a source-linked mathematical read-back of how \`BitcoinSupply.supply_bound\` and \`BitcoinSubsidy.issuance_bound\` yield \`BitcoinSupply.supply_lt_maxMoney\`.
- **Reproducible source checks**: the [CI workflow](.github/workflows/semantic-graph.yml) checks direct theorem references at their exact **pinned Lean source line numbers**, verifies imported-theorem candidates against the pinned Prove2me repository, runs the Python tests, and checks the viewer's JavaScript syntax. This is still **source-text evidence**, not kernel dependency extraction.

The Bitcoin graph contains **three direct source references** and **two import candidates**, explicitly distinguished. No semantic claim is marked independently reviewed. The RH graph is a previously documented source-level path, not a new discovery.

## Read-only Prove2me integration (v0.4)

The engine now supports an evidence-preserving progression from **local proposal-item IDs → actual platform theorem IDs → platform-recorded sketch dependencies**, without conflating them with Lean kernel-traced dependencies.

- [Integration guide](docs/PROVE2ME-INTEGRATION.md) explains the exact API endpoints, ID types, security controls and commands.
- [\`semantic_graph/prove2me.py\`](semantic_graph/prove2me.py) implements locally pinned proposal mapping, exact theorem-name lookup, cached theorem-detail binding, and decomposition import.
- [Bitcoin supply, with actual proposal-item IDs](examples/bitcoin_supply_proposal_linked.json) records three GitHub-sourced identifiers and repository-reported acceptance statuses. **They are not theorem IDs.**
- [Adapter regression tests](tests/test_prove2me_adapter.py) run without network calls using synthetic API responses.

All live Prove2me calls are **optional, authenticated GET-only**, with redirects disabled and credentials supplied only through a local environment variable. We have **not** connected a live Prove2me account or fetched its theorem records during this work. Platform sketches and natural-language annotations are not kernel certificates.

## Reusable semantic proof graph prototype (v0.3)

This repository now includes a **provider-neutral semantic graph engine** that can examine selected theorem paths from **Bitcoin/Prove2me** and **Alpöge's RH proof**. Both examples are pinned to full repository commit SHAs.

| Component | Purpose |
|---|---|
| [`semantic_graph/core.py`](semantic_graph/core.py) | Versioned JSON graph contract, integrity checks, dependency queries, Markdown and Mermaid renderers |
| [`semantic_graph/cli.py`](semantic_graph/cli.py) | Validate, visualize, explain, and verify imported-theorem candidates against a local pinned checkout |
| [Bitcoin supply example](examples/bitcoin_supply.json) | Actual theorem names, reachability assumptions and candidate imports from the [Prove2me Bitcoin formalization](https://github.com/pitimespi/prove2me) |
| [RH critical path example](examples/rh_critical_path.json) | Selected, manually traced theorem references in the RH mirror |
| [`tests/test_semantic_graph.py`](tests/test_semantic_graph.py) | Schema, edge semantics, provenance, and regression checks |
| [Design and usage](docs/SEMANTIC-GRAPH.md) | Trust model, extension points, limitations, and next milestones |

Run locally from this repository (Python 3.10+; standard library only):

```sh
python3 -m semantic_graph.cli validate examples/bitcoin_supply.json
python3 -m semantic_graph.cli validate examples/rh_critical_path.json
python3 -m semantic_graph.cli validate examples/bitcoin_supply_proposal_linked.json
python3 -m semantic_graph.cli mermaid examples/rh_critical_path.json > rh.mmd
python3 -m semantic_graph.cli report examples/bitcoin_supply.json --target supply_cap > bitcoin-supply.md
python3 -m unittest discover -s tests -v
```

The Bitcoin fixture marks edges as **`import_candidate`**, because the referenced proof file imports these published theorem stubs; import alone does not establish a genuine proof-term dependency. RH fixture edges are **`source_reference`**, not independently extracted kernel dependencies. There are **no** `kernel_dependency` edges in either fixture. An edge's interpretation is a separately versioned human-reviewable annotation, initially `draft`. Two independent reviewers are required before an annotation may be marked `independent_review`.

This project is *not* currently integrated with the Prove2me platform's private APIs and has not been submitted to its maintainers. The engine is an experimental research prototype, not a Lean theorem prover, formal certificate checker, or guarantee of mathematical truth. **Community outreach remains on hold.**

## Contents

- [`audit/AUDIT-001.md`](audit/AUDIT-001.md): source-grounded read-back of the top-level RH / GRH theorem path.
- [`audit/AUDIT-002.md`](audit/AUDIT-002.md): the `every_character_of_literature_of_vWin` interface, explicit inputs, and priority questions for understanding its central theorem application.
- [`audit/REVIEW-QUEUE.md`](audit/REVIEW-QUEUE.md): risk-ranked work items and evidence criteria.
- [`audit/PROVENANCE.md`](audit/PROVENANCE.md): exact pinned source and limitations.
- [`graph/`](graph/): 11-declaration illustrative source-level graph and metadata, **not** a proof-term DAG.
- [`tools/rh_audit.py`](tools/rh_audit.py): read-only static source scanner (Python standard library).
- [`tests/`](tests/): unit tests covering synthetic source snippets.
- [`PUBLICATION.md`](PUBLICATION.md): release checklist and community-engagement hold.

## Source baseline

| Item | Pin |
|---|---|
| Third-party mirror | [`Deicyde/riemann-hypothesis`](https://github.com/Deicyde/riemann-hypothesis) |
| Audited mirror commit | [`e50d09817ad81469f737e8f637561e6ccf86c670`](https://github.com/Deicyde/riemann-hypothesis/tree/e50d09817ad81469f737e8f637561e6ccf86c670) |
| Lean | `leanprover/lean4:v4.33.1` |
| Mathlib | `0df444a360eaa60ab8c11dca51a86af692955474` |

See [`audit/PROVENANCE.md`](audit/PROVENANCE.md). The source mirror states that the original proof has no explicit reuse license, so **we do not redistribute its Lean code**. File-level source references are links only.

## Reproduce our limited scan

Clone the original mirror to a separate directory and pin it; do not compile untrusted proof code outside an isolated environment. This static scanner **does not execute Lean**.

```sh
git clone https://github.com/Deicyde/riemann-hypothesis.git
cd riemann-hypothesis
git checkout e50d09817ad81469f737e8f637561e6ccf86c670
cd ..
python3 rh-semantic-audit/tools/rh_audit.py --root riemann-hypothesis --out rh-static-results
python3 -m unittest discover -s rh-semantic-audit/tests -v
```

Replace `rh-semantic-audit` with your local checkout directory name. The scanner checks 11 selected declarations by name and a set of expected *textual references*. It does not expand tactics, inspect `.olean` dependencies, compute theorem closures, check axioms or establish mathematical correctness.

## Research context and prior work

- [Original announcement](https://alpo.ge/remark.pdf)
- [MIT verification status](https://math.mit.edu/~drew/grh/)
- [Deicyde's verification mirror and issue #3](https://github.com/Deicyde/riemann-hypothesis/issues/3): earlier independent top-level proof maps and source reduction. Our graph overlaps this prior work and is not presented as novel.
- [Distributed replay and Mathlib-only statement checking](https://github.com/rohanarun/alpoge-rh-replay/tree/main/audit): independent formal checks we do not reproduce.
- [Keith Adler's `rh-trim`](https://github.com/keithadler/rh-trim): dependency tracing and reduction research; its earlier reduction numbers were corrected after failed builds.
- [Prove2me review method](https://github.com/pitimespi/prove2me/blob/main/REVIEW.md): inspiration for blind source read-backs.

## Near-term research questions

1. What are the exact mathematical contents of `UpperTheory.Lit.every_character_of_theta_integrals_local_matching` and its prerequisites?
2. Which arguments use `OpenLiteratureStatements` and how are those fields actually discharged by upstream theorems?
3. Can two independent analysts produce matching, specialist-readable read-backs of the crucial source terms?
4. Can the boundary between a named lemma and its mathematical justification be made navigable without replacing kernel verification?

## License and attribution

Original audit text, metadata and scanner in this repository are made available under the MIT License (`LICENSE`). This license **does not** apply to linked third-party Lean sources or external research. The original proof and other researchers' independent work retain their own copyright and license terms.

**Engagement hold:** No upstream issues, pull requests, announcements, or invitations have been posted as part of preparing this repository. See `PUBLICATION.md`.