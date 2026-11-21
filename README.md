# RH Semantic Audit

**Active research focus: the claimed Lean formalization of the Riemann Hypothesis, exclusively.**  
**Version:** 0.9 · **Baseline:** third-party verification mirror at commit `e50d09817ad81469f737e8f637561e6ccf86c670`.

This project develops an **evidence-aware semantic proof graph** for the purported RH formalization announced by Levent Alpöge on November 20, 2026. It distinguishes the meaning of a formal theorem, the assumptions feeding it, source-text connections, and actual Lean kernel dependencies. The goal is to explain the mathematics *without overstating what source inspection has established*.

**This is not a verified proof of RH, an independent kernel replay, or an original discovery of the high-level theorem dependency chain.** All mathematical explanations remain provisional until independently reviewed.

## RH research artifacts

| Artifact | What it provides |
|---|---|
| [AUDIT-001](audit/AUDIT-001.md) | First read-back of the RH theorem chain |
| [AUDIT-002](audit/AUDIT-002.md) | The literature/theta theorem interface and its visible prerequisites |
| **[AUDIT-003](audit/AUDIT-003-OPEN-LITERATURE.md)** | Exact three-field inventory of `OpenLiteratureStatements`, construction at the `everyCharacter_of_row` boundary, and unresolved type compatibility |
| [RH semantic graph](examples/rh_critical_path.json) | Selected source-linked theorem nodes, human-readable assumptions and draft explanations |
| **[AUDIT-004](audit/AUDIT-004-ANALYTIC-BRIDGE.md)** | Source-confirmed seven-premise analytic bridge, primitive nonvanishing, and Euler-factor passage to all characters |
| [RH analytic subgraph](examples/rh_analytic_bridge.json) | Eight intermediate theorem nodes, seven source-confirmed theorem invocations, and provisional mathematical explanations |
| [Review queue](audit/REVIEW-QUEUE.md) | Prioritized mathematical and formal-methods checks |
| [Provenance](audit/PROVENANCE.md) | Pinned source, Lean and Mathlib versions, and trust boundaries |

## Principal finding so far

At the pinned [`OpenLiteratureStatements` definition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L211-L218), the proposition has three named fields:

1. `caraianiLocalGlobalDual : UpperTheory.One.M.Row`
2. `localLanglandsExists : UpperTheory.Zero.LLC.RecTExists`
3. `galoisRepOfPolarizedPairLit : UpperTheory.One.M.Row`

The first and third fields request the **same written proposition type**. At the [`everyCharacter_of_row` application](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean#L7-L8), the terms supplied are `h`, `UpperTheory.Zero.LLC.recTExists`, and `h`, together with a `VWin` value constructed from `h`.

That is a **source-level description of the interface**, not a proof that all mathematical content is valid or a substitute for Lean elaboration/kernel verification.

## New finding: the analytic passage to character nonvanishing

At [`UpperTheory.Lit.everyE₂`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/FockModels/EveryCharacterE.lean#L67-L71), seven explicit inputs—including theta-integral agreement, local matching, covolume, local Langlands and `VWin`—are used to conclude `UpperTheory.EveryCharacter`. The [`plugWin` theorem](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean#L8-L11) provides primitive-character zero-freeness, and [`imprimitive`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/Imprimitive.lean#L5-L35) extends it to general characters through nonzero Euler factors.

This is an explicit **local analytic subgraph**, **not yet an independently verified link** to `every_character_of_theta_integrals_local_matching`. See [AUDIT-004](audit/AUDIT-004-ANALYTIC-BRIDGE.md). All mathematical validity and kernel-dependency questions remain open.

## Research program

Our next original work is to produce an independently reviewable mathematical explanation of:

- the precise definitions and compatibility of `UpperTheory.One.M.Row`, `UpperTheory.GalStar.Row0b`, and `UpperTheory.Top.VWin`;
- the complete *elaborated* type and relevant assumptions of `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`;
- how those theta-integral and local-matching hypotheses lead to `UpperTheory.EveryCharacter`, then `RiemannHypothesis`.

A meaningful contribution must provide **more mathematical substance and evidence** than the earlier source-dependency maps. See the [related verification discussion](https://github.com/Deicyde/riemann-hypothesis/issues/3) and [Keith Adler's proof map](https://github.com/keithadler/rh-trim/blob/main/docs/PROOF-MAP.md).

## Explore the RH graph locally

The [offline viewer](viewer/index.html) has two RH views—the headline critical path and the analytic subgraph—and focuses on the RH graph and displays the mathematical statements, recorded prerequisites, evidence classes, source links and review status.

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/viewer/` in your browser.

The reusable engine remains in [`semantic_graph/`](semantic_graph/), with a JSON validator, report generation and a local browser viewer:

```sh
python3 -m semantic_graph.cli validate examples/rh_critical_path.json
python3 -m semantic_graph.cli validate examples/rh_analytic_bridge.json
python3 -m semantic_graph.cli mermaid examples/rh_critical_path.json > rh.mmd
python3 -m semantic_graph.cli report examples/rh_critical_path.json --target headline > rh-review.md
python3 -m semantic_graph.cli report examples/rh_analytic_bridge.json --target everyE2 > rh-analytic-review.md
python3 -m unittest discover -s tests -v
```

These are graph/schema and source-level checks, **not Lean compilation or proof validation**. No unlicensed Lean proof source is bundled.

## Scope and engagement

**All new research and proposed contributions concern RH only.** Older Bitcoin/Prove2me examples and direct-submission prototype files remain in Git history and the working tree as legacy engineering fixtures; they are **not part of the current research program**. They are not being submitted to Prove2me or developed further. See [historical material](docs/LEGACY.md).

There is **no active Prove2me RH submission** in this project, and the available API does not automatically install a semantic graph as a platform feature. No community issues, upstream pull requests, contacts or announcements are authorized at this stage.

If an API credential was previously shared in chat, it should be revoked and replaced; no credential is stored in this repository.
