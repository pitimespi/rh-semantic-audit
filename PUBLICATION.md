# RH Semantic Audit — publication and verification scope

**Current release:** v0.10, November 20, 2026  
**Only active subject:** claimed Lean formalization of the Riemann Hypothesis.

Repository: https://github.com/pitimespi/rh-semantic-audit

## Completed source-level investigation

- [AUDIT-003](audit/AUDIT-003-OPEN-LITERATURE.md): inventoried the three explicit fields of `OpenLiteratureStatements`, including the duplicated written proposition type in two fields.
- [AUDIT-004](audit/AUDIT-004-ANALYTIC-BRIDGE.md): traced an **analogous** seven-premise theorem `UpperTheory.Lit.everyE₂` through primitive-character nonvanishing and Euler factors. It is **not the demonstrated direct path** to the headline theorem.
- [AUDIT-005](audit/AUDIT-005-EXACT-THETA-BRIDGE.md): located the actual `every_character_of_theta_integrals_local_matching` theorem at the pinned mirror's `SiegelEisensteinSecondTermHypotheses.lean`, lines 69–73. Mapped its seven explicit caller arguments, definite-side `HypsAlt` construction, and its use of `every_character_of_green_v_win`.
- [Actual bridge graph](examples/rh_actual_bridge.json): twelve source-linked nodes and eleven named source-reference edges.
- [Headline graph](examples/rh_critical_path.json): includes a source-confirmed reference to the central theta theorem.
- [Viewer](viewer/index.html): offers the *actual central bridge* first, then the headline chain and the clearly labeled earlier analogous branch.

## Reproducibility

Baseline mirror commit: `e50d09817ad81469f737e8f637561e6ccf86c670`.

The latest completed GitHub Actions RH run is [44852085962](https://github.com/pitimespi/rh-semantic-audit/actions/runs/44852085962). It passed:

- **57 unit tests**;
- graph validation and generated reports;
- JavaScript viewer syntax checking;
- pinned textual correspondence checks for the three `OpenLiteratureStatements` fields, the earlier seven-edge analog branch, and **all eleven edges** of the actual central bridge.

These tests are **not** Lean elaboration, a full compilation, a kernel proof replay, a formal axiom audit, or independent mathematical acceptance of RH.

## Active research questions

1. Expand `UnitaryGroupThirdPlaceHypotheses` and `ThetaLocalInputs` field by field and trace their proof origins.
2. Explain the analytic construction `nonempty_hyps_definite_side_of_closed_bound` precisely, including its evaluation-grid and linked-family steps.
3. Expand `Row0b`, `Row`, `VWin`, `HypsAlt`, `CovolumeBoundOfX` and `RecTExists` into human-reviewed mathematical statements.
4. Obtain a Lean-elaborated type, axiom inventory and genuine proof-term dependency evidence for the critical theorems.

## Access, licensing, and engagement policy

No external Prove2me contribution, issue, PR, discussion, announcement, researcher contact, or other community engagement has been made. The earlier Bitcoin engineering fixtures remain inactive and are not part of the current research. No user credential is stored or used in GitHub automation.

No unlicensed original Lean proof files are redistributed by the audit.
