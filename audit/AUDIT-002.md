# AUDIT-002 — The literature/theta-to-nonvanishing interface

**Date:** 2026-11-20. **Status:** source-level inspection and first read-back only. Not a mathematical verification of the theorem, exhaustive hypothesis closure, or proof-term audit. All source locations refer to the pinned third-party verification mirror commit `e50d09817ad81469f737e8f637561e6ccf86c670`.

## 1. Exact theorem interface visible in the source

The declaration [`UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L810) has two explicit inputs:

- `O : UpperTheory.LiteratureTheorems.OpenLiteratureStatements`
- `hV : UpperTheory.Top.VWin`

Its conclusion is `UpperTheory.EveryCharacter`, the statement that Dirichlet L-functions do not vanish in `Re(s) > 1/2` except for the excluded trivial-character case.

The body invokes `UpperTheory.Lit.every_character_of_theta_integrals_local_matching` and supplies several named prerequisites. Visible supplied inputs include:

- `published_results_eigen O`
- `published_results_first O`
- the two components of `theta_integrals_agree_and_local_matching_of_literature O`
- a geometric/positivity construction `topCovolSlim2_use_alt_alt` assembled from several results, some derived from `O`
- `local_langlands_gl_recT_exists_of_literature O`
- the direct input `hV`

These are **names and syntactic application arguments**, not yet fully expanded mathematical hypotheses. Full elaboration can insert implicit arguments and typeclass instances.

## 2. Plain-language mathematical read-back

**Conditional statement:** Given a packaged collection of literature-related formal facts `O` and a formal automorphic-window witness `hV`, the code constructs the proposition that all complex Dirichlet L-functions under consideration are zero-free in the right half-plane `Re(s) > 1/2`, apart from the explicitly excluded trivial-character point. The proof is assembled by invoking a large pre-existing-in-this-development theorem whose name indicates a combination of theta-integral identities and local matching.

This is the precise limit of our source-level interpretation. Neither the word *literature* in the package name nor the theorem names alone establish whether a claimed result is valid, classical, newly derived, or merely assumed. These questions require inspecting each declaration and its type.

## 3. How the top-level result supplies the premises

[`MainConclusion.lean` L7-L11](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean#L7-L11) composes this theorem through `everyCharacter_of_row`:

- Its input is `h : UpperTheory.GalStar.Row0b (...)`.
- It passes a constructed value of `OpenLiteratureStatements` containing `h`, `UpperTheory.Zero.LLC.recTExists`, and `h` to the literature theorem.
- It constructs `VWin` by applying `UpperTheory.One.vwin_of_row h`.
- A separate theorem then supplies the `Row0b` input via `UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter`.

It is thus **incorrect** to describe the literature package as an *unconditionally assumed axiom* from this trace alone. The source explicitly provides terms for its inputs. Whether all mathematical content is established in an intended way requires deeper checking; independent kernel replay is separate from this read-back.

## 4. Relation to existing investigations

The chain containing `every_character_of_theta_integrals_local_matching` and `every_character_of_green_v_win`, and the fact that `OpenLiteratureStatements` is constructed rather than left as a headline hypothesis, were already reported in [`Deicyde/riemann-hypothesis` issue #3](https://github.com/Deicyde/riemann-hypothesis/issues/3) and [`rh-trim`](https://github.com/keithadler/rh-trim). This document does **not** claim priority for those observations.

The value we aim to add in later revisions is a **human-reviewed account of what the formal premises mean mathematically**, with independently checked definitions, references and explicit limits.

## 5. Open review questions

| ID | Question | Required evidence | Status |
|---|---|---|---|
| LT-01 | What is the exact *type* and field structure of `OpenLiteratureStatements`? | Pinned definition and human-readable explanation of every field | Open |
| LT-02 | What is the exact statement of `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`? | Complete declaration type, including implicit parameters and instances, from Lean environment | Open |
| LT-03 | What does `UpperTheory.Top.VWin` assert? | Expanded formal definitions and independent mathematical read-back | Open |
| LT-04 | Which `published_results_*` facts are needed and where are they proved? | Pinned theorem/type inventory and proof-term dependency report | Open |
| LT-05 | Which theta-integral/local-matching equalities supply the zero-free conclusion? | Stepwise expert argument matched to source, not naming-based inference | Open |
| LT-06 | Are any literature facts genuinely unresolved assumptions? | Independent axiom audit/Lean environment check, not a regex scan | Open |

**Provisional verdict:** The interface can be located, summarized, and linked reproducibly. The source alone does not yet support a mathematically complete interpretation. No defect is claimed.
