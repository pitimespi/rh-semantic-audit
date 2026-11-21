# Why reachable Bitcoin UTXO supply stays below MAX_MONEY

The statement of `BitcoinSupply.supply_lt_maxMoney` is **relative to the formal chain model**: for any state `S` with `hR : BitcoinBlockV2.Reachable S`, the value `BitcoinSupply.totalValue S.utxo` is strictly less than `MAX_MONEY`. It does not quantify over arbitrary ledgers or, by itself, establish behavioral equivalence with every Bitcoin Core implementation.

The proof combines two previously established results. First, `BitcoinSupply.supply_bound S hR` gives the invariant

```
totalValue S.utxo + genesisSubsidy ≤ issued S.nextHeight.
```

Second, `BitcoinSubsidy.issuance_bound S.nextHeight` bounds scheduled issuance strictly below the monetary cap. After rewriting `issued` and the denomination constants, the result is `issued S.nextHeight < MAX_MONEY`. Because `genesisSubsidy` is the natural-number amount coerced to an integer, it is nonnegative. Hence

```
totalValue S.utxo
  ≤ totalValue S.utxo + genesisSubsidy
  ≤ issued S.nextHeight
  < MAX_MONEY.
```

The last inequality is discharged by Lean's Presburger arithmetic tactic `omega` after the named facts are made available.

The supporting supply invariant is proved by induction on the `Reachable` relation. In the genesis case the initial ledger, issuance schedule, and genesis subsidy definitions establish the base inequality. For an accepted block extending a reachable state, `BitcoinSupply.block_supply` limits the increase in spendable UTXO value to the next subsidy. `BitcoinBlockV2.apply_spec` and the issuance recurrence connect the updated chain height to the scheduled subsidy, closing the inductive step.

This is a read-back of the formal argument's structure, not an independent audit of all modeled Bitcoin consensus conditions. In particular, `Reachable` and the definitions of `totalValue`, `issued`, and `MAX_MONEY` determine the exact scope of the result.

Source: [theorem statement](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Theorems/Thm_BitcoinSupply_supply_lt_maxMoney.lean), [final proof (lines 311–321)](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_lt_maxMoney.lean#L311-L321), and [supply invariant proof (lines 311–329)](https://github.com/pitimespi/prove2me/blob/64f338540bb1d4264d4f101d5dd656e290fa0afb/Solutions/Sol_BitcoinSupply_supply_bound.lean#L311-L329).
