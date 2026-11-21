# AUDIT-007 — A conditional hypothesis is discharged: the Minkowski bridge

**Pinned source:** `e50d09817ad81469f737e8f637561e6ccf86c670`, third-party mirror of the claimed 2026 RH formalization.  
**Status:** focused source-level semantic finding, with one closed concern and several open mathematical review obligations. **No independent Lean compilation, kernel replay, or discovery of a proof flaw.**

## Finding: the conditional `MinkDiv` hypothesis is used with an explicit supplier

A conditional in the global-witness constructor appears potentially weak unless its antecedent is available:

- [`UpperTheory.Top.classSel`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/ClassSel.lean#L14-L25) concludes, among other data, `DC.MinkDiv → ExD 𝒜 cT`, rather than unconditionally returning `ExD 𝒜 cT`.
- [`GlobalTheory.Fc.nonempty_hyps_of_allRows_alt`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/NonemptyHypsOfAllRows.lean#L49-L60) passes this implication into the global `HypsAlt` witness, whose `hEx` field is itself conditional: `MinkDiv → UpperTheory.Top.ExS 𝒜 cT` at [`Hyps.lean` line 26](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/Hyps.lean#L26).
- Much later in the proof, the *actual RH branch* uses [`UpperTheory.Top.shape_closed_link_n_of_green`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/TopShape.lean#L33-L53) to build `TopG`. Its analytic sub-lemma `GlobalTheory.Top.designExists_of_tuSize_aux4n_litThin` explicitly uses the conditional `hEx` in the form **`hEx minkowski_bound_rat`**, at [`LinkEx.lean` line 35](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/LinkEx.lean#L35).

Thus the source **does not merely assume** that `MinkDiv` is inhabited at that point: it supplies the named term `minkowski_bound_rat` to discharge the antecedent.

The supplier is a named theorem [`minkowski_bound_rat : PI.MinkowskiBoundQ`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Formalism/PeriodIntegrals/OrbitalBoundsConclusion/MinkowskiQ.lean#L6), itself defined from [`PI.MkQ.minkowskiBoundQ`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Formalism/PeriodIntegrals/UnitaryGroupMassFormula/MinkowskiTorsionFree/Lattice.lean#L124-L129). It is a rational finite-linear-group cardinality/divisibility bound, not simply a fabricated proof variable.

**Evidence boundary:** the exact syntactic application is verified. We have not independently used Lean to expand the alias/coercion relating the short name `MinkDiv` to `PI.MinkowskiBoundQ`, nor verified the upstream Minkowski theorem's complete dependency/axiom inventory. The conclusion is therefore **“source-identified discharge of the apparent conditional,” not “the mathematics is independently proved.”**

## Why this qualifies as a useful RH semantic annotation

Our [AUDIT-006](AUDIT-006-GLOBAL-WITNESS.md) found that the central theorem builds a 46-field `HypsAlt` structure. A field of the form `A → B` can be vacuously inhabited if `A` is false; claiming that `B` is available without finding a proof of `A` would be an invalid semantic explanation.

The reviewed source does supply a term to `hEx` at the downstream use. This is an **actual cross-module assumption-discharge path** that a direct source-level theorem dependency graph misses:

```text
classSel
  │ yields MinkDiv → ExD
  ▼
nonempty_hyps_of_allRows_alt
  │ sets HypsAlt.hEx : MinkDiv → ExS
  ▼
shape_closed_link_n_of_green
  │ invokes designExists_of_tuSize_aux4n_litThin
  ▼
hEx minkowski_bound_rat
  ▲
  │ minkowski_bound_rat : PI.MinkowskiBoundQ
  │   derived from PI.MkQ.minkowskiBoundQ
  └── explicit source-level proof supplier
```

**Crucial correction:** There is no justified claim of a missing `MinkDiv` hypothesis or counterexample based merely on its conditional appearance. This specific concern is now **resolved at source level**.

## Remaining high-risk mathematical questions

1. **`DefiniteSideCondition`**: [the definition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/DefiniteSideCondition.lean#L25-L35) is a nested implication with substantial hypotheses, including `CovolumeOntoIsometryConditions`, `PassIn3`, `DivisionCompatibilityDataThreeSided` and a `DivTied3` premise. We have not shown that these antecedents are jointly satisfiable for the selected family, nor that the resulting `RowsU` conclusion is instantiated in the final zero-freeness argument. A condition being syntactically nontrivial does not establish that its implication is nonvacuous.
2. **Field transfer:** The [46-field constructor](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/NonemptyHypsOfAllRows.lean#L55-L101) carries row witnesses through lambda wrappers, `Closed.sub` restrictions and one `Classical.choice` inside `selJ`. We still need elaborated types and a mathematical read-back of those transformations.
3. **Underlying row selection:** [`UpperTheory.Top.classSel`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/ClassSel.lean#L14-L25) uses `RowL.elim`, `Row.elim`, and selection/construction theorems to choose a family. The exact semantic nonemptiness and intended properties of the chosen class remain to be established independently.
4. **Kernel/axiom audit:** Source-level calls do not establish transitive proof-term dependencies. A Lean export should confirm the actual type of the `MinkDiv` argument and the upstream axiom surface.

## Suggested contribution to the Prove2me RH mission

**Type:** research reference / source-level semantic clarification, **not** proof, counterexample, `proof_gap`, or `missing_hypothesis` report.

**Claim:** In the pinned claimed RH formalization, the apparent `MinkDiv` conditional on the `HypsAlt.hEx` field is supplied by a named Minkowski-bound theorem in the definite-side shape argument. The actual unresolved mathematical review is the nonvacuity and use of `DefiniteSideCondition` and the selected row obligations.

**Release discipline:** If posted, link this report and exact source lines, and state clearly that the RH proof has not been independently verified. Do not tag the observation as a proof error. The mission's existing Mathlib goal is not being claimed solved.

**Verdict:** One apparent hypothesis-discharge question is answered at the source level; one more precise nonvacuity/row-selection review target is identified. This is a publishable, bounded research annotation, *not* a solution of RH.
