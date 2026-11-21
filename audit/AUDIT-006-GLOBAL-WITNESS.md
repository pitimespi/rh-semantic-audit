# AUDIT-006 — From theta/local matching to a 46-field global hypothesis witness

**Pinned source:** third-party RH verification mirror commit `e50d09817ad81469f737e8f637561e6ccf86c670`  
**Status:** reproducible **source-level theorem read-back and record-constructor audit**. No Lean elaboration, proof-term dependency extraction, independent mathematical proof, or claim of an RH defect.

## 1. The exact theorem whose mathematics needs reviewing

[SiegelEisensteinSecondTermHypotheses.lean lines 44–68](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L44-L68) declares `UpperTheory.Lit.nonempty_hyps_definite_side_of_closed_bound`.

It accepts **six initial inputs** (a `UnitaryGroupThirdPlaceHypotheses` package, `ThetaLocalInputs`, `ThetaIntegralsAgree`, `LocalMatching`, `CovolumeBoundOfX`, and `RecTExists`) plus an explicit **parameter-indexed `LinkedAt` bound**. Its conclusion is:

```lean
Nonempty (GlobalTheory.Fc.HypsAlt S0.NL GlobalTheory.Fc.DefiniteSideCondition)
```

The theorem does not directly prove the Riemann Hypothesis. The enclosing [central theta theorem](AUDIT-005-EXACT-THETA-BRIDGE.md) uses this result to obtain an inhabited global hypothesis structure, then supplies it to the Green/window nonvanishing theorem.

**Mathematical interpretation:** the conclusion packages a broad family of chosen objects, selection functions, row inequalities, counting statements, local/global hypotheses, and geometric constraints. Source inspection alone does not establish why those conditions are jointly realizable.

## 2. The constructive route in the source

The proof in [SiegelEisensteinSecondTermHypotheses.lean lines 45–68](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L45-L68) takes these steps, each with a named theorem application and a concrete resulting Lean object.

| Step and source | Object constructed | Source-level role |
|---|---|---|
| [SiegelEisensteinSecondTermHypotheses.lean lines 47–48](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L47-L48) | `hS : FunctionalsSeparate` | From Howe-unramified input and Siegel–Weil convergence |
| [SiegelEisensteinSecondTermHypotheses.lean lines 49–50](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L49-L50) | `hRat : S0.RowRat` | Uses theta agreement, local matching, and functionals separation through a test-vector construction |
| [SiegelEisensteinSecondTermHypotheses.lean lines 51](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L51) | `hFit : ConstantFunctionFits` | Fourier coefficient/function fit derived from the same matching inputs and a global lower-bound statement |
| [SiegelEisensteinSecondTermHypotheses.lean lines 52–54](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L52-L54) | `⟨CF1,hCF1⟩` | Evaluation-grid theorem provides a real threshold and a condition for each larger grid parameter |
| [SiegelEisensteinSecondTermHypotheses.lean lines 55–56](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L55-L56) | `⟨CF0,hCF0⟩` | Another real threshold, now for a parameterized functional `LinkedAt` condition |
| [SiegelEisensteinSecondTermHypotheses.lean lines 57](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L57) | `hEv` | Instantiates grid evidence at `max CF0 CF1` |
| [SiegelEisensteinSecondTermHypotheses.lean lines 58–62](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L58-L62) | `hOpen1,hMono,hOpenA` | Obtains an open-parameter assertion and transports it through a stronger-extension comparison |
| [SiegelEisensteinSecondTermHypotheses.lean lines 63–64](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L63-L64) | `hFun` | Functional `LinkedAt` evidence at the common parameter |
| [SiegelEisensteinSecondTermHypotheses.lean lines 65–67](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L65-L67) | `hL3` | Covolume-related `LinkedAt` evidence at the same extension |
| [SiegelEisensteinSecondTermHypotheses.lean lines 68](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L68) | `Nonempty HypsAlt` | Applies `hypotheses_nonempty_of_unramified_exponents_alt` with `hEv`, `hN`, `hFun`, `hL3` |

The use of `max CF0 CF1` is a **quantifier/parameter synchronization** step: the two threshold witnesses can both be applied at their common upper bound. It is not, by itself, the analytic content.

## 3. The next level: unramified exponents, a row bundle, and a selected family

The next theorem, [`GlobalTheory.Fc.S0.StageU.hypotheses_nonempty_of_unramified_exponents_alt`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/HypothesesNonemptyOfUnramifiedExponents.lean#L41-L59), first constructs a large-unramified-exponent bundle, extracts geometric/Galois inputs, transports a family norm bound, and obtains an `AllRowsAlt` package from `allRows_of_open0_alt`.

At [line 57](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/HypothesesNonemptyOfUnramifiedExponents.lean#L57) it calls `GlobalTheory.Fc.nonempty_hyps_of_allRows_alt` to produce the inhabited global witness. The `AllRowsAlt` package is itself a `Prop` structure with **26 named fields** documented at [AllRows.lean lines 12–39](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/AllRows.lean#L12-L39). Its fields concern counting, selected rows, period and twist conditions, bounds, and other named predicates. *Those labels are still not independently expanded into their complete mathematical definitions.*

The constructor theorem [`nonempty_hyps_of_allRows_alt`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/NonemptyHypsOfAllRows.lean#L19-L101) combines those row conditions, invokes `UpperTheory.Top.classSel` to select a family and associated data, and fills a `HypsAlt` record.

## 4. Exact 46-field correspondence

[`GlobalTheory.Fc.HypsAlt`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/Hyps.lean#L22-L90) is explicitly a dependent `Type 1` structure with **46 named fields**, not just an abbreviation for `True`. The [final record literal](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/NonemptyHypsOfAllRows.lean#L55-L101) assigns **46 field names in the same order**.

The [machine-readable field ledger](../examples/rh_witness_fields.json) records, for each name:

- its declaration location;
- its constructor-assignment location;
- a syntactic strategy such as pass-through, lambda construction, closed-family restriction, or classical choice;
- `syntax_only` review status and pinned source links.

The proof contains a visible classical choice at `selJ`, where a dependent selection witness is extracted inside a function. This use of Lean's built-in classical choice is **not, by itself, evidence of an unsound axiom or proof defect**. It instead marks a precise spot for interpreting *what witness is chosen and which existing existential proposition makes that choice available*.

Other fields are transferred via `Formalism.MainNotions.Pk.Closed.sub`, which should be audited as restrictions of closed-family predicates and not automatically identified with the unchanged original predicates.

**What the equality of field names establishes:** the exact source-level record has no *missing or extra named assignments*. It does **not** establish that an elaborated Lean term type-checks, that any prerequisite theorem holds mathematically, or that a consequence is non-vacuous. Those stronger checks require a Lean environment and mathematical review.

## 5. The definite-side condition is a real dependent predicate, not a magic label

[`DefiniteSideCondition.lean` lines 25–35](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/DefiniteSideCondition.lean#L25-L35) defines `GlobalTheory.Fc.DefiniteSideCondition` using several hypotheses on families, isometries, division compatibility, integer lattices and number facts. It requires a `RowsU` conclusion when named `DivTied3` and identity-of-data hypotheses hold.

This is not syntactically the literal `True`. However, source-level inspection has **not** shown that its antecedents can actually hold for the objects of interest, or that its consequences have the intended analytic interpretation. Vacuity and definitional strength remain questions to check.

## 6. Where the review effort now belongs

| Priority | Exact technical question | Required completion evidence |
|---|---|---|
| First | Does `allRows_of_open0_alt` establish the 26 required row conditions with intended, non-vacuous mathematical meaning? | Full theorem type, origin of each field, and an independent read-back of the critical predicates |
| First | Does `classSel` preserve these conditions in the selected `HypsAlt` family? | Exact elaborated type and focused study of `RowL`, `Closed.sub`, `selJ`, and the selection witness |
| Second | What is the mathematical content of `evaluation_grid_of_join` and `linked_bundles_l3_of_open_alt`? | Identify their underlying theta integrals, local matching, geometry and bound hypotheses |
| Second | Can the `DefiniteSideCondition` antecedents be satisfied for the constructed families? | Inspect definitions and prove or exhibit appropriate non-vacuity/useful instantiations |
| Third | Is the actual proof free of unexpected axioms beyond accepted Lean foundations? | Kernel-built axiom report and proof-term dependency extraction; not GitHub text search |

**Status:** The source-level assembly is now mapped down to a **26-field row proposition** and a **46-field dependent witness**. There is no new claim that RH is valid or invalid. The mathematical soundness of the row-to-witness transformations is the next independent review boundary.
