# RH Semantic Audit

**Active research focus: the claimed Lean formalization of the Riemann Hypothesis, exclusively.**  
**Version:** 0.12 · **Baseline:** third-party verification mirror at commit `e50d09817ad81469f737e8f637561e6ccf86c670`.

This project develops an **evidence-aware semantic proof graph** for the purported RH formalization announced by Levent Alpöge on November 20, 2026. It distinguishes the meaning of a formal theorem, the assumptions feeding it, source-text connections, and actual Lean kernel dependencies. The goal is to explain the mathematics *without overstating what source inspection has established*.

**This is not a verified proof of RH, an independent kernel replay, or an original discovery of the high-level theorem dependency chain.** All mathematical explanations remain provisional until independently reviewed.

## RH research artifacts

| Artifact | What it provides |
|---|---|
| [AUDIT-001](audit/AUDIT-001.md) | First read-back of the RH theorem chain |
| [AUDIT-002](audit/AUDIT-002.md) | The literature/theta theorem interface and its visible prerequisites |
| **[AUDIT-003](audit/AUDIT-003-OPEN-LITERATURE.md)** | Exact three-field inventory of `OpenLiteratureStatements`, construction at the `everyCharacter_of_row` boundary, and unresolved type compatibility |
| [RH semantic graph](examples/rh_critical_path.json) | Selected source-linked theorem nodes, human-readable assumptions and draft explanations |
| **[AUDIT-005: exact central theorem](audit/AUDIT-005-EXACT-THETA-BRIDGE.md)** | Locates the actual seven-premise theorem, all seven caller arguments, and the definite-side Green/window route |
| **[Actual RH theorem bridge graph](examples/rh_actual_bridge.json)** | Twelve nodes and eleven source-confirmed theorem invocations along the central route |
| **[AUDIT-006: global witness assembly](audit/AUDIT-006-GLOBAL-WITNESS.md)** | Follows the theta/local-matching premises through the grid, linked-bundle and selected-row stages |
| **[AUDIT-007: Minkowski conditional discharge](audit/AUDIT-007-MINKOWSKI-DISCHARGE.md)** | Source-verified closure of one apparent conditional-witness concern, with exact remaining non-vacuity obligations |
| [Prove2me RH resource contribution](docs/PROVE2ME-RH-RESOURCE.md) | A bounded research article, preview-first API publisher and tests; **not yet submitted to Prove2me** |
| **[RH witness-assembly graph](examples/rh_witness_assembly.json)** | Sixteen named proof-step nodes and fifteen pinned source-reference edges |
| **[26→46 field correspondence ledger](examples/rh_witness_fields.json)** | All 26 upstream `AllRowsAlt` field names map to field names in the 46-field `HypsAlt` constructor; correspondence is syntactic only |
| [AUDIT-004](audit/AUDIT-004-ANALYTIC-BRIDGE.md) | Earlier analogous seven-premise theorem `everyE₂`; not the direct central theorem route |
| [Earlier analytic subgraph](examples/rh_analytic_bridge.json) | Comparative theorem route, not demonstrated as a direct dependency of the headline |
| [Review queue](audit/REVIEW-QUEUE.md) | Prioritized mathematical and formal-methods checks |
| [Provenance](audit/PROVENANCE.md) | Pinned source, Lean and Mathlib versions, and trust boundaries |

## Principal finding so far

At the pinned [`OpenLiteratureStatements` definition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L211-L218), the proposition has three named fields:

1. `caraianiLocalGlobalDual : UpperTheory.One.M.Row`
2. `localLanglandsExists : UpperTheory.Zero.LLC.RecTExists`
3. `galoisRepOfPolarizedPairLit : UpperTheory.One.M.Row`

The first and third fields request the **same written proposition type**. At the [`everyCharacter_of_row` application](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean#L7-L8), the terms supplied are `h`, `UpperTheory.Zero.LLC.recTExists`, and `h`, together with a `VWin` value constructed from `h`.

That is a **source-level description of the interface**, not a proof that all mathematical content is valid or a substitute for Lean elaboration/kernel verification.

## Main finding: exact central theorem and its seven inputs

The previously missing declaration `UpperTheory.Lit.every_character_of_theta_integrals_local_matching` is now located at [`SiegelEisensteinSecondTermHypotheses.lean` lines 69–73](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L69-L73). It takes `UnitaryGroupThirdPlaceHypotheses`, `ThetaLocalInputs`, theta agreement, local matching, `CovolumeBoundOfX`, `RecTExists`, and `VWin`.

The [literature caller](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L810-L814) supplies **all seven explicit arguments** through pinned, named source terms. The central theorem uses `nonempty_hyps_definite_side_of_closed_bound` and `every_character_of_green_v_win`, followed by a primitive-to-general-character Euler-factor argument.

This is **not the same** as the similarly named and earlier [`everyE₂`](audit/AUDIT-004-ANALYTIC-BRIDGE.md), which uses different geometric/local-Langlands assumptions. [AUDIT-005](audit/AUDIT-005-EXACT-THETA-BRIDGE.md) and the [actual graph](examples/rh_actual_bridge.json) document the correction. The direct source-level theorem path is now known; its mathematical validity and fully elaborated dependencies are **not** independently checked.

## New source-level result: 26 upstream row fields → 46 downstream witness fields

The central theorem calls [`nonempty_hyps_definite_side_of_closed_bound`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L44-L68). We traced its two grid thresholds, `max CF0 CF1`, functional and covolume `LinkedAt` evidence, and the theorem producing `Nonempty HypsAlt`.

That stage obtains a [26-field `AllRowsAlt : Prop`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/AllRows.lean#L12-L39). **All 26 of its field names reappear** in the downstream [46-field `HypsAlt : Type 1`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/Hyps.lean#L22-L90). The final record constructor assigns all 46 names. Source-pinned CI compares the field names and their declaration/assignment lines and checks all 15 named theorem calls in the [witness graph](examples/rh_witness_assembly.json).

**These are name correspondences, not proof-term dependencies or evidence of mathematical equivalence.** In particular, some fields are transformed by closed-family restriction and one uses `Classical.choice`. See [AUDIT-006](audit/AUDIT-006-GLOBAL-WITNESS.md) for the exact bounds and review questions.

## Focused research contribution prepared for Prove2me (v0.12)

[**AUDIT-007**](audit/AUDIT-007-MINKOWSKI-DISCHARGE.md) resolves a specific semantic ambiguity in the actual RH route: the `MinkDiv → ExS` component of the global witness is used downstream with an explicit proof supplier `minkowski_bound_rat`, not an assumed or uninstantiated antecedent. The report traces the source reference back to a named rational-group Minkowski-bound theorem, with eight source-line checks.

The remaining mathematical questions concern the non-vacuity and adequacy of `DefiniteSideCondition` and the selected row conditions. This is a **source-level research reference**, not a new Lean theorem, proof, missing-hypothesis claim, or independent verification of RH.

The official [Prove2me Riemann Hypothesis mission](https://prove2.me/missions/The_Riemann_Hypothesis) supports user-submitted **resources**. We prepared the [bounded article payload](contributions/rh_minkowski_resource.json), a [secure, duplicate-safe API publisher](semantic_graph/post_rh_resource.py), and [local setup instructions](docs/PROVE2ME-RH-RESOURCE.md). **No Prove2me API write was made from this chat:** there is no authenticated Prove2me connection, and the earlier disclosed key should be revoked and replaced. Run the documented publication command with a new, locally supplied key to post the resource.

## Research program

Our next original work is to produce an independently reviewable mathematical explanation of:

- the precise definitions and compatibility of `UpperTheory.One.M.Row`, `UpperTheory.GalStar.Row0b`, and `UpperTheory.Top.VWin`;
- the complete *elaborated* type and relevant assumptions of `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`;
- how those theta-integral and local-matching hypotheses lead to `UpperTheory.EveryCharacter`, then `RiemannHypothesis`.

A meaningful contribution must provide **more mathematical substance and evidence** than the earlier source-dependency maps. See the [related verification discussion](https://github.com/Deicyde/riemann-hypothesis/issues/3) and [Keith Adler's proof map](https://github.com/keithadler/rh-trim/blob/main/docs/PROOF-MAP.md).

## Explore the RH graph locally

The [offline viewer](viewer/index.html) provides four RH views: **actual central theta bridge** (recommended), **46-field witness assembly**, headline critical path, and the earlier analogous analytic route. Each shows statements, prerequisites, evidence classes, source links and review status.

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/viewer/` in your browser.

The reusable engine remains in [`semantic_graph/`](semantic_graph/), with a JSON validator, report generation and a local browser viewer:

```sh
python3 -m semantic_graph.cli validate examples/rh_critical_path.json
python3 -m semantic_graph.cli validate examples/rh_actual_bridge.json
python3 -m semantic_graph.cli validate examples/rh_witness_assembly.json
python3 -m semantic_graph.cli validate examples/rh_analytic_bridge.json
python3 -m semantic_graph.cli mermaid examples/rh_critical_path.json > rh.mmd
python3 -m semantic_graph.cli report examples/rh_critical_path.json --target headline > rh-review.md
python3 -m semantic_graph.cli report examples/rh_actual_bridge.json --target outer > rh-actual-review.md
python3 -m tools.rh_witness_fields --fetch-pinned --ledger examples/rh_witness_fields.json
python3 -m tools.rh_analytic_check --fetch-pinned --graph examples/rh_witness_assembly.json
python3 -m tools.rh_minkowski_check --fetch-pinned
python3 -m semantic_graph.post_rh_resource  # local preview; no API access
python3 -m semantic_graph.cli report examples/rh_analytic_bridge.json --target everyE2 > rh-analogous-review.md
python3 -m unittest discover -s tests -v
```

These are graph/schema and source-level checks, **not Lean compilation or proof validation**. No unlicensed Lean proof source is bundled.

## Scope and engagement

**All new research and proposed contributions concern RH only.** Older Bitcoin/Prove2me examples and direct-submission prototype files remain in Git history and the working tree as legacy engineering fixtures; they are **not part of the current research program**. They are not being submitted to Prove2me or developed further. See [historical material](docs/LEGACY.md).

There is **no active Prove2me RH submission** in this project, and the available API does not automatically install a semantic graph as a platform feature. No community issues, upstream pull requests, contacts or announcements are authorized at this stage.

If an API credential was previously shared in chat, it should be revoked and replaced; no credential is stored in this repository.
