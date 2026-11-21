# Risk-ranked mathematical review queue

RH-only review plan. It borrows generic evidence and read-back methods from earlier formal verification work, but no other subject remains an active research target. This is not a completed independent mathematical proof review.

## Priority A — first independent review

**A1. Expand `OpenLiteratureStatements` at the composition boundary — source-level inventory COMPLETE, elaborated mathematical interpretation OPEN.** [AUDIT-003](AUDIT-003-OPEN-LITERATURE.md) identifies its three exact fields: two of type `UpperTheory.One.M.Row`, and one of type `UpperTheory.Zero.LLC.RecTExists`. The proof passes `⟨h, UpperTheory.Zero.LLC.recTExists, h⟩`. Next: explain the relationship of `Row0b` and `Row` with actual Lean elaboration; classify all field-defining prerequisites, rather than assuming they are automatically discharged mathematically.

**A2. Explain `UpperTheory.Lit.every_character_of_theta_integrals_local_matching` — source type and argument map COMPLETE; substantive mathematical/Lean review OPEN.** [AUDIT-005](AUDIT-005-EXACT-THETA-BRIDGE.md) locates the actual seven-input theorem, maps every explicit caller argument and traces its use of `nonempty_hyps_definite_side_of_closed_bound` and `every_character_of_green_v_win`. The earlier [AUDIT-004](AUDIT-004-ANALYTIC-BRIDGE.md) describes a similar *different* `everyE₂` route. Next: expand the new theorem's structured hypotheses and the proof obligations of the nonempty-HypsAlt constructor; check elaborated dependencies and mathematical interpretation.

**A2b. Audit the `AllRowsAlt` → `HypsAlt` witness transformation — source-field map COMPLETE, mathematical meaning OPEN.** [AUDIT-006](AUDIT-006-GLOBAL-WITNESS.md) follows 15 named helper calls from the theta/local-matching inputs into `Nonempty HypsAlt`, and the [field ledger](../examples/rh_witness_fields.json) verifies all 26 upstream row field names recur among the 46 downstream field names, with 46 corresponding assignments. The most important remaining work is independent review of `allRows_of_open0_alt`, `classSel`, the `Closed.sub` restrictions, the selected join's `Classical.choice`, and the non-vacuity of `DefiniteSideCondition`. A source-name match is not a proof of type or mathematical equivalence.

**A3. Trace `UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter`.** Identify what `Row0b recT` means, how the theta-lift and Galois representation constructions establish it, and any assumptions encoded in types or instances.

## Priority B — independent formal-methods review

**B1. Verify semantics of the headline five statements.** Cross-compare the independently compiled `Challenge.lean` with `Main.lean` and Mathlib. A passing Comparator has stronger significance than a source-text match.

**B2. Document metaprogramming and axiom surfaces.** Independent verifier's notes identify `kexactB`, `kcopy`, and direct assignment of terms; these raise the importance of independent kernel replay, rather than independently proving an exploit or unsoundness.

**B3. Generate the *elaborated* dependency DAG.** Use Lean/Mathlib environment tools, not regular expressions, and record the exact versions and source SHA used.

## Priority C — expert mathematical exposition

**C1. Write the argument in prose using ordinary theorem/proof structure.** Find natural groups of mathematical lemmas. Ask specialists to assess whether any genuinely novel theorem can be stated compactly.

**C2. Include adversarial read-backs.** One reviewer sees only the formal statement; another sees independently selected mathematical background without the source proof. Compare, then resolve disagreements at the definition level.

**C3. Track audit outcomes explicitly.** Mark findings as `verified source match`, `explanation incomplete`, `needs independent Lean check`, `actual counterexample`, or `discharged`; do not call every missing explanation an error.

## Done means

A review item is complete only when it has a pinned source URL, an exact statement, human-readable interpretation, all important hypotheses enumerated, explicit evidence for its verdict, and the limits of that evidence.

## What transfers from Prove2me

- Blind read-backs and source correspondence: **strong transfer**.
- Risk-ranked spot reviews and independently repeated audits: **strong transfer**.
- Differential input/output vectors against Bitcoin Core: **weak transfer**; abstract propositions have no executable reference implementation.
- Independent checkers, pinned revisions, and axiom audits: **strong transfer**, but don't duplicate existing expensive runs without clear new value.

## Current baseline work and non-duplication

See [`AUDIT-002.md`](AUDIT-002.md) for the literature/theta interface and [`AUDIT-003`](AUDIT-003-OPEN-LITERATURE.md) for the three-field hypothesis inventory. Keith Adler's public dependency map already traces the five-theorem `EveryCharacter` chain; the independent replay project already checks headline statement definitions. Our proposed work must add *mathematical interpretation* or new independently reproducible evidence, not relabel existing maps as new research.
