# AUDIT-001 — From `everyCharacter` to `riemannHypothesis`

**Scope:** Independent source inspection of a selected theorem chain, 2026-11-20.  
**Status:** Preliminary, source-backed *read-back*; not a Lean kernel check, a complete dependency closure, a peer-reviewed mathematical proof, or independent confirmation of Alpöge's claim.

## Source baseline

Public verification mirror: [`Deicyde/riemann-hypothesis`](https://github.com/Deicyde/riemann-hypothesis/tree/e50d09817ad81469f737e8f637561e6ccf86c670), commit `e50d09817ad81469f737e8f637561e6ccf86c670`.

This is a third-party mirror of the author's published archive with supplemental verification files. The repository records the original 14-part archive's SHA-256 separately; see `PROVENANCE.md`. No assertion is made that the author committed the mirror revision.

## Precise semantic read-back of the intermediate claim

The declaration [`UpperTheory.EveryCharacter`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean#L13) is a proposition asserting:

For every positive modulus `N` (via `[NeZero N]`), every complex-valued Dirichlet character `χ` modulo `N`, and every complex `s`, if `Re(s) > 1/2` and `(χ ≠ 1 or s ≠ 1)`, then the Mathlib Dirichlet `LFunction χ s` does not vanish.

Mathematically, this is

\[
\forall N\ge1\;\forall\chi\pmod N\;\forall s\in\mathbb C:\quad
\left(\operatorname{Re}(s)>\tfrac12\ \land\ (\chi\ne1\ \lor\ s\ne1)\right)
\implies L(s,\chi)\ne0.
\]

The proposition includes imprimitive characters. It does **not** say that every sort of automorphic, Artin, or Dedekind L-function is zero-free there. It does not assert nonvanishing at a trivial character's excluded `s=1`. Its meaning ultimately relies on Mathlib's `DirichletCharacter.LFunction` and its associated type-class instances.

## Source-linked theorem chain

| Step | Source | Precise role |
|---|---|---|
| Galois bridge | [`RowSrc.lean` L6](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean#L6) | Constructs `galoisLocalGlobalStrong_recParameter` using `galoisRepresentations_of_thetaLift` and `tLiftK`. This is an upstream premise, not the final RH argument. |
| Window construction | [`VwinOfRow.lean` L4](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean#L4) | Produces a `VWin` witness from a `Row0b` hypothesis. |
| Literature/theta bridge | [`EveryCharacterOfLiteratureOfVWin.lean` L810](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L810) | Takes `OpenLiteratureStatements` and `VWin` to `EveryCharacter`, invoking `every_character_of_theta_integrals_local_matching` and many concrete prerequisites. High priority for mathematical explanation. |
| Composition | [`MainConclusion.lean` L7](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean#L7) | `everyCharacter_of_row` combines the literature/theta result with a constructed package of inputs and `vwin_of_row`. |
| Discharge upstream premise | [`MainConclusion.lean` L10](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean#L10) | `everyCharacter` applies `everyCharacter_of_row` to `galoisLocalGlobalStrong_recParameter`, yielding the unconditional Lean proposition. |
| Name the result | [`MainTheorems.lean` L7](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Supplements/Kernels/MainTheorems.lean#L7) | Defines `allChi` as `UpperTheory.FinalTheorems.everyCharacter`. |
| Zeta bridge | [`CritLine.lean` L29](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Formalism/GammaFactorNonvanishing/CritLine.lean#L29) | `rh_of_every` specializes to modulus one and uses `LFunction_modOne_eq` to obtain the required zeta nonvanishing. |
| Functional equation | [`RhOfRight.lean` L5](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Formalism/GammaFactorNonvanishing/RhOfRight.lean#L5) | `rh_of_right` applies the zeta functional equation, nonvanishing of auxiliary factors, and a trichotomy to place nontrivial zeros on the line. |
| Conclude | [`MainTheorems.lean` L9](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Supplements/Kernels/MainTheorems.lean#L9), [`Main.lean` L4](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Main.lean#L4) | `rhOfAll` is passed directly to `riemannHypothesis : RiemannHypothesis`. |

This table records exact visible source relationships, not the entire dependency DAG. A Lean-generated report is needed to confirm elaborated dependencies and transitive assumptions.

## Important reasoning distinction

The final `rh_of_right` bridge is understandable independently of the very large proof: it derives the exclusion of zeros on one side of the critical line from an assumed zero-free half-plane; the functional equation reflects zeros from the other side. This argument cannot establish RH *on its own*. It depends entirely on actually obtaining the nonvanishing input `allChi`.

## First interpretation checkpoint

The central composition step is only two source-level declarations, but hides extensive mathematics. `everyCharacter_of_row` supplies a constructed `OpenLiteratureStatements` term and a `VWin` term. The literature theorem itself calls `every_character_of_theta_integrals_local_matching`, and the upstream proof constructs Galois data through theta lifts.

A useful semantic audit should expand **the exact type and fields** of `OpenLiteratureStatements`, explain which declared result supplies each field, and determine which prerequisites are newly proven versus already present in Mathlib. That mapping has **not yet been completed** in v0.1.

## Known limitations and acceptance criteria

- **Confirmed by direct source reading:** the eleven selected declaration locations and the top-level source-text composition.
- **Not done:** independent elaborated dependency extraction, exhaustive axiom inspection, kernel replay, validation of mathematical content of large upstream lemmas, or an independent expert review.
- **Formal checking status:** the external verification mirror reports independent checks; their validity and exact scope should be assessed from the checker-produced artifacts, not from this report.
- **Acceptance criterion for next revision:** a type-accurate, noncircular field-by-field read-back of `OpenLiteratureStatements`, accompanied by source locations and a verified elaborated dependency closure of `everyCharacter_of_row`.

**Preliminary verdict:** The headline mathematical claim and the final bridge are legible and structurally faithful on inspection. The upstream mathematical mechanism remains the major unreviewed surface of this project. This is an audit-progress statement, **not** a verdict that RH has been proved.