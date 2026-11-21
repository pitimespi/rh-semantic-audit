# AUDIT-004 — The analytic passage from theta inputs to Dirichlet L-function nonvanishing

**UPDATE (subsequent audit):** [AUDIT-005](AUDIT-005-EXACT-THETA-BRIDGE.md) located the actual central theorem and showed that it calls a **different** definite-side `HypsAlt` bridge. The `everyE₂` graph here is a useful comparative analytic route, **not an established direct dependency of the headline proof**. The missing source-level connection identified in this earlier report has now been resolved **as a different route**, although mathematical correctness and elaborated kernel dependencies remain unverified.

**Baseline:** third-party RH mirror commit `e50d09817ad81469f737e8f637561e6ccf86c670`.  
**Status:** source-level theorem-type and proof-composition review; **not** independent Lean elaboration, kernel replay, or mathematical validation. All semantic interpretations are provisional.

## Key finding

A source-located intermediate theorem, `UpperTheory.Lit.everyE₂`, takes **seven explicitly named inputs** and returns `UpperTheory.EveryCharacter`. We can follow its directly visible proof through a chain of smaller theorems, including a separate argument extending a primitive-character nonvanishing statement to **all Dirichlet characters**.

The central high-level theorem `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`, invoked later in `EveryCharacterOfLiteratureOfVWin.lean`, has **not** yet been located as a complete elaborated declaration. Therefore the exact mapping from its caller's arguments into these seven inputs remains **unverified**; the graph in this report is a *source-confirmed local subgraph*, not a new connected proof path from the headline to the leaf mathematics.

## 1. The seven inputs of `everyE₂`

At [`EveryCharacterE.lean` lines 67–71](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/FockModels/EveryCharacterE.lean#L67-L71), the theorem `UpperTheory.Lit.everyE₂` explicitly accepts:

| Binder | Lean proposition/type | Role visible in this source |
|---|---|---|
| `P` | `S0.HypothesesUE` | A structured package of spectral/global ingredients; its `greenRegularCharacters` and `nLink` fields are used directly |
| `F` | `GlobalTheory.FunPr.Hypotheses₂` | A second structured package used to build the intermediate analytic hypotheses |
| `hA` | `GlobalTheory.IndefiniteRowSideFullHecke.WeilTensorModels.ThetaIntegralsAgree` | Theta-integral agreement condition |
| `hM` | `GlobalTheory.IndefiniteRowSideFullHecke.WeilTensorModels.LocalMatching` | Local-matching condition |
| `hX` | `GlobalTheory.CovTop.CovolX` | Covolume/geometric condition |
| `hL` | `GlobalTheory.Published.LocalLanglandsGL` | Local Langlands proposition |
| `hV` | `UpperTheory.Top.VWin` (unqualified as `VWin` in namespace) | Analytic window witness |

The output `UpperTheory.EveryCharacter` is precisely the [nonvanishing proposition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean#L13-L14): for every positive level, every complex Dirichlet character and complex `s` strictly right of the critical line, the L-function does not vanish, apart from the stated trivial-character exceptional case.

**What has not been checked:** the full definition of `VWin`, all fields of `P` and `F`, and whether implicit arguments or elaborated instances introduce additional obligations.

## 2. From theta hypotheses to a nonempty global hypothesis witness

The auxiliary theorem [`UpperTheory.Lit.hypsE₂`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/FockModels/EveryCharacterE.lean#L41-L65) accepts `P,F,hA,hM,hX,hL` and an additional bound on a local/global parameter indexed by each real `cDep`. Its result is an inhabited global hypothesis package, `Nonempty (Hyps S0.NL DRS)`.

Within its body, the source constructs:

- a separation result for functionals using `F` and selected fields of `P`;
- a rationality/row object based on theta agreement and local matching;
- a suitable analytic function at the global parameter;
- linked family data at a common maximum of two thresholds;
- the final `Nonempty` conclusion by applying `nonempty_hyps_of_classicalTheoremsUE`.

This is a **sequence of named formal steps**, not an independent proof that all the analytic estimates or identities hold. The actual definitions of these properties need separate explanation.

The final bound supplied by `everyE₂` is constructed by `UpperTheory.N.boundAtTwoThree_at_prm_of_prints` using `P.nLink` and `hL`, rather than appearing as a separate explicit binder in `everyE₂`.

## 3. Converting global hypotheses and a window into primitive nonvanishing

The [`everyE₂` body](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/ThetaCorrespondence/FockModels/EveryCharacterE.lean#L70-L71) calls `UpperTheory.Top.plugAll` with:

1. a Green-type premise `GlobalTheory.GreenBridge.green_of_regular P.greenRegularCharacters`;
2. the given `hV` window;
3. the witness provided by `hypsE₂`.

The [`UpperTheory.Top.plugWin` theorem](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean#L8-L11) turns those ingredients into `Formalism.HC.ZeroFreeAll`. It invokes the theorem [`zeroFreeAll_of_topG`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/ZeroFreeAllOfTopG.lean#L26-L38) with parameter `la = 3/2`, an appropriate `TopG` obtained from a shape theorem, and a supplied host-existence statement for each primitive character.

The latter host-existence statement uses [`UpperTheory.Top.supplyChi`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/SupplyChi.lean#L8-L15). The visible type of `supplyChi` asks for `VWinAt ψ 401`, with output `HostExW (3/2) (GChi ψ).req`. At the call site, `hV ψ` fills this input. This supplies **source-level evidence** that the `VWin` witness acts as a family of character-indexed window witnesses; the actual full definition of `VWin` is still unexpanded.

## 4. The primitive-to-imprimitive step is an explicit Euler-factor argument

[`UpperTheory.Top.imprimitive`](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/Imprimitive.lean#L5-L35) accepts `ZeroFreeAll` and concludes the full statement that an L-function for any Dirichlet character cannot vanish in the right half-plane, subject to the trivial-character exception.

Its proof:

1. passes from a general character `χ` to its primitive character of conductor `χ.conductor`;
2. uses `ZeroFreeAll` to establish nonvanishing for the primitive L-function;
3. invokes `DirichletCharacter.LFunction_changeLevel` to express the original L-function through the primitive one and finitely many Euler factors;
4. checks each correction factor cannot vanish: the character value has norm at most 1, and for primes `p>1` and `Re(s)>1/2>0`, `|p^{-s}|<1`;
5. concludes nonvanishing of the product.

This step is **mathematically intelligible from the supplied source** and does not require the entire theta/lift proof to state it. It is also standard analytic-number-theoretic reasoning; we claim neither novelty nor priority.

The [`plugAll` definition](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean#L16-L18) simply composes `plugWin` and `imprimitive`.

## 5. Local source-confirmed dependency map

```text
P, F, theta agreement, local matching, covolume,
local Langlands, and parameter bound
                    │
                    ▼
                  hypsE₂
                    │ Nonempty global hypotheses
                    ▼
Green premise ───► plugAll ◄── VWin
                    ▲
                    │ uses plugWin and imprimitive
            plugWin → ZeroFreeAll
                    │
                    ▼
                 imprimitive
                    │
                    ▼
       EveryCharacter (all Dirichlet characters)
```

The diagram is *schematic*: `plugAll` composes `plugWin` and `imprimitive`, while `everyE₂` supplies it `hypsE₂` and other inputs. The exact, source-evidenced edges are recorded separately in [`examples/rh_analytic_bridge.json`](../examples/rh_analytic_bridge.json).

## 6. Remaining verification boundaries

| ID | Open question | Evidence needed |
|---|---|---|
| AB-01 | Where is the exact declaration `every_character_of_theta_integrals_local_matching`, and how does it call or specialize `everyE₂`? | Pinned source declaration, *fully elaborated* type, and actual proof-term dependency if available |
| AB-02 | What is `VWin`, and how does it support `VWinAt ψ 401`? | Definitional expansion, then a mathematical statement |
| AB-03 | What are all the fields of `S0.HypothesesUE` and `GlobalTheory.FunPr.Hypotheses₂`? | Source-pinned structure inventories and individual proof origins |
| AB-04 | Why is `Nonempty (Hyps S0.NL DRS)` sufficient for the `TopG` construction? | Inspect `GlobalTheory.Fc.shape_of`, `TopShape`, and its associated type instances |
| AB-05 | Are the analytic identities and spectral hypotheses sound and obtained without unreviewed axioms? | Independent Lean axiom audit and mathematics, not regex/source naming |
| AB-06 | How do `Row0b`, `Row`, and the `OpenLiteratureStatements` package connect to this analytic layer? | Precise expanded statement and explanation at their composition boundary |

**Verdict:** We now have a concrete local analytic subchain that explains *what kinds of mathematical inputs* lead to character nonvanishing, and a legible standard step from primitive to general characters. It is **not** a proof that those analytic inputs are true, nor a kernel audit of the claimed RH proof.
