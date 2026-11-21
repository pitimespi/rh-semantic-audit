# AUDIT-005 — Exact central theta theorem and its seven supplied premises

**Date:** 2026-11-20 · **Pinned mirror:** `e50d09817ad81469f737e8f637561e6ccf86c670`.  
**Evidence grade:** direct source-type and theorem-application inspection. **No Lean elaboration, kernel replay, or independent mathematical acceptance.**

## Finding: the central theorem is now located

The precise declaration `UpperTheory.Lit.every_character_of_theta_integrals_local_matching` is at [`SiegelEisensteinSecondTermHypotheses.lean` lines 69–73](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L69-L73).

It has seven explicit inputs. Crucially, **this theorem does not directly invoke `UpperTheory.Lit.everyE₂`**. The two declarations are similar in mathematical intent, but the actual central theorem uses **different hypothesis types** and an alternate bridge through `UpperTheory.Top.every_character_of_green_v_win` and `UpperTheory.Lit.nonempty_hyps_definite_side_of_closed_bound`.

That distinction corrects a major gap in the earlier [AUDIT-004](AUDIT-004-ANALYTIC-BRIDGE.md), which presented `everyE₂` as a local analogue but deliberately did not claim it was on the headline's direct dependency route.

## 1. Exact premises of the actual theorem

The following table maps the seven explicit binders in the [central theorem](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L69-L73) to the *actual terms passed* by [`every_character_of_literature_of_vWin`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L810-L814).

| Input | Lean proposition/type | Term supplied by caller |
|---|---|---|
| `P` | `GlobalTheory.Fc.S0.UnitaryGroupThirdPlaceHypotheses` | `UpperTheory.LiteratureTheorems.published_results_eigen O` |
| `F` | `GlobalTheory.FunPr.ThetaLocalInputs` | `UpperTheory.LiteratureTheorems.published_results_first O` |
| `hA` | `GlobalTheory.IndefiniteRowSideFullHecke.WeilTensorModels.ThetaIntegralsAgree` | First projection of `theta_integrals_agree_and_local_matching_of_literature O` |
| `hM` | `GlobalTheory.IndefiniteRowSideFullHecke.WeilTensorModels.LocalMatching` | Second projection of the same paired result |
| `hX` | `GlobalTheory.CovTop.CovolumeBoundOfX` | `SelfIntersectionVolumeEstimates.topCovolSlim2_use_alt_alt` applied to fifteen explicitly supplied mathematical premises |
| `hL` | `UpperTheory.Zero.LLC.RecTExists` | `UpperTheory.LiteratureTheorems.local_langlands_gl_recT_exists_of_literature O` |
| `hV` | `UpperTheory.Top.VWin` | The caller's `hV`, itself constructed at the higher `everyCharacter_of_row` boundary |

**Source checks of intermediate types:** `published_results_eigen` returns the exact `UnitaryGroupThirdPlaceHypotheses` type [at line 666](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L666); `published_results_first` returns `ThetaLocalInputs` [at line 727](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L727); the theta/local-matching result returns a conjunction of those exact proposition types [at line 565](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L565); and `local_langlands_gl_recT_exists_of_literature` returns `RecTExists` [at line 313](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L313).

The covolume builder's output type, `CovolumeBoundOfX`, is visible at [`TopCovolSlim2Use.lean` line 16](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/TopCovolSlim2Use.lean#L16). The source-level argument list is lengthy, but the names and number of arguments should not be confused with independent verification of their correctness.

## 2. What the central theorem actually does

The theorem's body is a direct composition:

- It creates a Green-type premise using `GlobalTheory.GreenBridge.green_of_regular P.greenRegularCharacters`.
- It forwards the supplied `hV : VWin`.
- It constructs `Nonempty (GlobalTheory.Fc.HypsAlt S0.NL GlobalTheory.Fc.DefiniteSideCondition)` with `UpperTheory.Lit.nonempty_hyps_definite_side_of_closed_bound`, passing `P,F,hA,hM,hX,hL`.
- It discharges the remaining parameter-indexed bound with `UpperTheory.N.boundAtTwoThree_linked_of_recT P.nLink`, applied to `parametersOfDependence hL cDep`. The defining result is visible at [`At23OfAll.lean` lines 24–26](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/At23OfAll.lean#L24-L26).

The intermediate theorem [`nonempty_hyps_definite_side_of_closed_bound` lines 44–68](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean#L44-L68) uses theta agreement, local matching, covolume and local Langlands in a chain of rationality, function-fitting, evaluation-grid, extension and linked-bundle constructions to establish nonemptiness of the global hypothesis package. This is where significant analytic content is still awaiting expert interpretation.

## 3. The actual zero-free conclusion

At [`TopPlug.lean` lines 16–18](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/TopPlug.lean#L16-L18), `UpperTheory.Top.every_character_of_green_v_win` produces `UpperTheory.EveryCharacter` by applying `UpperTheory.Top.imprimitive` to `zero_free_all_of_green_v_win`.

At [`TopPlug.lean` lines 12–15](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/TopPlug.lean#L12-L15), `zero_free_all_of_green_v_win` establishes primitive-character zero-freeness using:

- a Green-to-shape theorem `shape_closed_link_n_of_green`;
- the shape/hypotheses bridge `forall_goal_of_shape_of_hyps`;
- per-character host existence `supplyChi ψ (hV ψ)`;
- the underlying primitive zero-freeness theorem `zeroFreeAll_of_topG` at `la = 3/2`.

Finally, [`imprimitive`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/Imprimitive.lean#L5-L35) obtains general-character nonvanishing through primitive reduction and nonzero Euler correction factors.

## 4. Why this matters semantically

The source-level causal structure is now:

```text
  published_results_eigen O   published_results_first O
                  \            /
             theta agreement / local matching
                     covolume bound
                     RecTExists
                         |
                nonempty_hyps_definite_side_of_closed_bound
                         |
                    global HypsAlt
                         |
      Green + VWin ---> every_character_of_green_v_win
                         |
                   EveryCharacter
                         |
   (central every_character_of_theta_integrals_local_matching)
                         |
              every_character_of_literature_of_vWin
                         |
                everyCharacter_of_row
                         |
                   EveryCharacter
                         |
                        RH
```

This text diagram is explanatory, **not a claim that every named upstream theorem has been independently audited**. The [machine-readable actual-bridge graph](../examples/rh_actual_bridge.json) records concrete source-reference edges.

## 5. Non-equivalence of the earlier analogous `everyE₂` path

The earlier [`UpperTheory.Lit.everyE₂` theorem](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/FockModels/EveryCharacterE.lean#L67-L71) has inputs with the *same intuitive categories* but different types:

| Category | Earlier `everyE₂` | Actual central theorem |
|---|---|---|
| First hypothesis package | `S0.HypothesesUE` | `S0.UnitaryGroupThirdPlaceHypotheses` |
| Second package | `GlobalTheory.FunPr.Hypotheses₂` | `GlobalTheory.FunPr.ThetaLocalInputs` |
| Geometric bound | `GlobalTheory.CovTop.CovolX` | `GlobalTheory.CovTop.CovolumeBoundOfX` |
| Local Langlands premise | `GlobalTheory.Published.LocalLanglandsGL` | `UpperTheory.Zero.LLC.RecTExists` |
| Global hypothesis output | `Nonempty (Hyps S0.NL DRS)` | `Nonempty (HypsAlt S0.NL DefiniteSideCondition)` |
| Last bridge to all characters | `plugAll` | `every_character_of_green_v_win` |

The source demonstrates a **different direct composition path**. It does not show that the earlier theorem is absent from every *transitive* proof-term dependency; proving absence requires a Lean-generated dependency trace.

## 6. Still open

1. Expand `UnitaryGroupThirdPlaceHypotheses` and `ThetaLocalInputs` field by field, then verify the mathematical interpretation of the published-results constructors.
2. Investigate the analytic validity of the `nonempty_hyps_definite_side_of_closed_bound` constructions, especially evaluation-grid and linked-bundle arguments.
3. Expand `CovolumeBoundOfX`, `RecTExists`, `VWin` and the `HypsAlt` fields.
4. Obtain exact *elaborated* types and proof-term/axiom information from a Lean 4 environment. Source presence and GitHub CI tests alone do not establish this.
5. Trace `Row0b` and `Row` definitions and verify their role in constructing the three fields of `OpenLiteratureStatements`.

**Verdict:** The source-level seven-premise central theorem, its seven caller arguments, and the direct Green/window/primitive-to-all-character composition are now located and mapped. The mathematical correctness of these inputs and their formal transitive dependencies remain unverified.
