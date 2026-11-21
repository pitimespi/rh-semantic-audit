# BITCOIN-001 — Why the UTXO supply ceiling follows

**Audit:** preliminary source-grounded mathematical read-back, **not** an independently kernel-checked proof.  
**Source baseline:** [pitimespi/prove2me at \`64f338540bb1d4264d4f101d5dd656e290fa0afb\`](https://github.com/pitimespi/prove2me/tree/64f338540bb1d4264d4f101d5dd656e290fa0afb).  
**Semantic status:** \`draft\` — this report is not independently peer-reviewed.

## Claim and exact scope

[The formal theorem statement](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Theorems/Thm_BitcoinSupply_supply_lt_maxMoney.lean) asserts, for a chain state \`S\` and a witness \`hR : BitcoinBlockV2.Reachable S\`:

\`\`\`lean
BitcoinSupply.totalValue S.utxo < MAX_MONEY
\`\`\`

This is **not** a claim about arbitrary coin ledgers or a proof that all real-world Bitcoin implementations are correct. It is a model-relative invariant over states reachable in the formal Bitcoin consensus transcription.

The proof file lives at [\`Solutions/Sol_BitcoinSupply_supply_lt_maxMoney.lean\`](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_lt_maxMoney.lean#L311-L321).

## Three mathematical ingredients

Let:

- \`U = BitcoinSupply.totalValue S.utxo\`, the value of the currently spendable UTXO set in the model;
- \`G = BitcoinSupply.genesisSubsidy\`, the genesis subsidy;
- \`I = BitcoinSupply.issued S.nextHeight\`, total issuance to that height;
- \`M = MAX_MONEY\`, the formal monetary cap.

The direct proof cites **two separately named theorems**:

1. [\`BitcoinSupply.supply_bound\`](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Theorems/Thm_BitcoinSupply_supply_bound.lean) supplies \`U + G ≤ I\`, assuming the chain state is reachable. It is invoked explicitly in the [solution at line 314](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_lt_maxMoney.lean#L314).
2. [\`BitcoinSubsidy.issuance_bound\`](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Theorems/Thm_BitcoinSubsidy_issuance_bound.lean) supplies the strict issuance cap for arbitrary heights. It is invoked explicitly at [line 315](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_lt_maxMoney.lean#L315).

The proof also establishes \`0 ≤ G\` by \`Int.natCast_nonneg\`, and normalizes the issuance and \`MAX_MONEY\` representations.

Thus elementary linear arithmetic yields:

\`\`\`text
U + G ≤ I
      I < M
  0 ≤ G
──────────
      U < M
\`\`\`

The concluding Lean proof uses \`omega\`; that tactic is **not** the source of the mathematical insight, only the final arithmetic discharge.

## Why \`supply_bound\` holds for all reachable states

[\`Sol_BitcoinSupply_supply_bound.lean\` lines 311–329](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_bound.lean#L311-L329) proves the invariant by induction on \`BitcoinBlockV2.Reachable S\`.

- **Genesis:** the initial state and issuance definitions establish the initial inequality.
- **Inductive step:** a validated next block transforms \`S\` to \`S'\`. The proof explicitly invokes [\`BitcoinSupply.block_supply\` at line 321](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_bound.lean#L321), constraining the increase in UTXO value by at most that height's subsidy.
- **Height/issuance correspondence:** \`BitcoinBlockV2.apply_spec\` is used to derive the new height and to establish the issuance recurrence. The inductive inequality then extends to the new state.

This explains the progression: **local per-block minting constraint → invariant across reachable chains → global UTXO supply ceiling.**

## Source-level dependency classification

| Candidate relationship | Evidence in proof source | Classification |
|---|---|---|
| \`block_supply → supply_bound\` | Explicit theorem application at supply_bound solution line 321 | \`source_reference\` |
| \`supply_bound → supply_lt_maxMoney\` | Explicit theorem application at final solution line 314 | \`source_reference\` |
| \`issuance_bound → supply_lt_maxMoney\` | Explicit theorem application at final solution line 315 | \`source_reference\` |
| \`issuance_bound → supply_bound\` | Imported by the supply_bound solution; not directly invoked by the visible final invariant proof | \`import_candidate\` |
| \`reachable_wellFormed → supply_bound\` | Imported by the supply_bound solution; explicit use has not been established in this first trace | \`import_candidate\` |

These are **not kernel-exported dependency edges**, and the semantic significance of imported helpers remains provisional. The [structured fixture](../examples/bitcoin_supply_proposal_linked.json) preserves these evidence kinds.

## What would make this review independent?

A second reviewer should:

1. Read the theorem types and proof source *without* this explanation, then independently state the argument and hypotheses.
2. Check that the model's \`totalValue\`, \`issued\`, \`MAX_MONEY\`, \`ChainState\`, and \`Reachable\` definitions mean exactly what this account assumes.
3. Examine the stated model limits in [Prove2me's existing review guide](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/REVIEW.md) and identify any limit relevant to the financial invariant.
4. Distinguish a passing **platform submission**, local Lean build with stub imports, and an independent complete formal replay.
5. Only then record an independent review decision on the graph edge annotations.

**Current verdict:** mathematically coherent proof strategy visible in pinned source; no new theorem or defect claimed; independent review pending.
