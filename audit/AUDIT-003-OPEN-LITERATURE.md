# AUDIT-003 — The actual assumptions packaged as OpenLiteratureStatements

**Source revision:** third-party RH verification mirror `e50d09817ad81469f737e8f637561e6ccf86c670`  
**Status:** complete **source-text field inventory**; incomplete mathematical interpretation and Lean-elaborated audit.  
**New in this report:** exact source definitions and argument positions, with an explicit distinction between theorem hypotheses and independently verified mathematical truth.

## 1. The package is a proposition with three fields

At [the pinned `OpenLiteratureStatements` definition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L211-L218), the source declares a structure in `Prop` with these fields:

| Field of `OpenLiteratureStatements` | Required proposition | What is established by this source inspection |
|---|---|---|
| `caraianiLocalGlobalDual` | `UpperTheory.One.M.Row` | Exact field type as written |
| `localLanglandsExists` | `UpperTheory.Zero.LLC.RecTExists` | Exact field type as written |
| `galoisRepOfPolarizedPairLit` | `UpperTheory.One.M.Row` | Exact field type as written |

The first and third fields have the **same source-level type**. This means the package does not expose three *distinct* top-level proposition types; it has three named fields, two of which request a proof of the same proposition. Those field *names* may suggest different mathematical motivations, but the types, not the names, determine what is required at this interface.

The package is **not** an unproved top-level axiom simply because its name includes the word “Open”; that claim would require a separate actual axiom/dependency analysis.

## 2. The public proof supplies all three slots syntactically

The [pinned `everyCharacter_of_row` theorem](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean#L7-L8) has one explicit input of type `UpperTheory.GalStar.Row0b (fun h rc => UpperTheory.Zero.LLC.IsRecT h rc)`, and applies the literature theorem with this constructor-like tuple:

| Field in order | Term supplied in `everyCharacter_of_row` | Source-level observation |
|---|---|---|
| `caraianiLocalGlobalDual` | `h` | Reuses the theorem's `Row0b` witness |
| `localLanglandsExists` | `UpperTheory.Zero.LLC.recTExists` | Supplies a separately named theorem |
| `galoisRepOfPolarizedPairLit` | `h` | Reuses the same `Row0b` witness |

The second argument of `every_character_of_literature_of_vWin` is constructed by `UpperTheory.One.vwin_of_row h`, also shown on line 8.

**Important limit:** This is a textual construction and a mapping of explicit arguments to named fields, not an independent check of inferred coercions, reducibility or elaboration. Although both occurrences of `h` are passed into fields written as `UpperTheory.One.M.Row`, the input's written type is `Row0b (...)`. We still must inspect the definitions and Lean environment to explain the compatibility rather than assume these are definitionally identical.

## 3. The local Langlands slot is backed by a named proof

The imported [`recTExists` theorem](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/Foundations/LocalLanglands/LocalCentralUnits/RecTExists.lean#L20-L29) is explicitly declared to establish `UpperTheory.Zero.LLC.RecTExists`, and its body begins by constructing witnesses from named prerequisites, including an artin-like existence step, a cuspidal existence step, and local Langlands extension constructions. This source observation tells us it is **provided as a theorem**, not merely an undeclared constant.

Its mathematical validity and its full transitive axiom dependencies are **not** established by reading these opening lines.

The row witness is supplied at a separate boundary by [`UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean#L4-L7), which constructs a `Row0b recT` value by applying `galoisRepresentations_of_thetaLift` to `tLiftK`.

We have **not** demonstrated exactly how the literal `recT` in this declaration specializes to the lambda in `everyCharacter_of_row`; that requires definition expansion or a Lean environment report.

## 4. Why the package matters for RH

The [literature/theta interface](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean#L810-L814) accepts `OpenLiteratureStatements` and `VWin` and returns `UpperTheory.EveryCharacter`. This is an upstream nonvanishing statement, not the RH conclusion itself.

The latter is [defined as a proposition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean#L13-L14) asserting that for every positive modulus (via `[NeZero N]`), every complex Dirichlet character and complex number strictly right of the line `Re(s)=1/2`, the corresponding L-function does not vanish, excluding the stated trivial-character exceptional point.

The central `every_character_of_theta_integrals_local_matching` theorem is *invoked* at the literature interface. We have not independently extracted its fully elaborated theorem type or explained why its theta-integral and local-matching inputs suffice.

## 5. What is genuinely new in this review

This report adds a **three-field, source-pinned hypothesis inventory** to our audit and resolves the specific open question of how `OpenLiteratureStatements` is populated **syntactically** at this interface.

It does **not** claim priority for discovering the theorem chain, constructing this triple, or noticing that `OpenLiteratureStatements` is instantiated; these facts were already discussed in [Deicyde/riemann-hypothesis issue #3](https://github.com/Deicyde/riemann-hypothesis/issues/3).

## 6. Next questions with precise completion criteria

| ID | Question | What would count as an answer | Current |
|---|---|---|---|
| RH-01 | Are the two `Row` fields merely duplicates at the type level? | Lean expansion and definitional equivalence analysis of `UpperTheory.One.M.Row` and `Row0b (...)` | Source-level identical types; elaborated check pending |
| RH-02 | What exact mathematical facts do `Row0b`, `Row`, and `VWin` express? | Human mathematical read-back derived from their definitions, not their names | Open |
| RH-03 | Does `recTExists` rely on any undeclared axiom or new primitive? | Independent Lean axiom audit of the theorem's transitive proof term | Open |
| RH-04 | What is the fully elaborated type of `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`? | Exact Lean `#check`/environment extraction and hypothesis classification | Open |
| RH-05 | Why does the central theta-integral/local-matching input imply zero-freeness? | Stepwise independent mathematical explanation grounded to precise Lean declarations | Open |

**Verdict:** the three explicit premises and their source-level construction are now documented. This is a reproducible *interface audit*, not a proof of RH or independent acceptance of the mathematical claim.
