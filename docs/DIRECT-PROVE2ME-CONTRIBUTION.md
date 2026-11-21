# Contributing an explanation directly to Prove2me

This is the first **real platform-write workflow** for the semantic proof graph experiment. It updates the natural-language **explanation** on an accepted Prove2me submission owned by your account.

The official API documents `PATCH /api/v1/submissions/:id` with an `explanation` field for the submission's original creator. See [official proof-submission guidance](https://github.com/prove2me/prove2me_workspace/blob/main/references/prove.md#edit-the-explanation).

**No contribution has been submitted automatically.** ChatGPT's connected tools can edit our GitHub repository, but the current execution environment cannot make authenticated network requests to `prove2.me`. This CLI can be executed from your own workstation after you have obtained and safely supplied a *new* API key.

## First contribution candidate

The draft [Bitcoin supply-cap explanation](../contributions/bitcoin_supply_lt_maxMoney_explanation.md) is based on exact theorem references in the owner's [pinned Bitcoin formalization](https://github.com/pitimespi/prove2me/tree/64f338540bb1d4264d4f101d5dd656e290fa0afb).

The full [independent-readback workpaper](../audit/BITCOIN-001-SUPPLY.md) distinguishes imported theorem candidates from directly invoked source-level theorems. Its content is provisional; the write-up should be reviewed before publication.

The proposed target is **the submission for** `BitcoinSupply.supply_lt_maxMoney`. It is **not** a new mathematical theorem and requires no Lean build or proof replacement.

## Preview without publishing

From your local `rh-semantic-audit` checkout, prompt for a key invisibly (it should never be included in a command line argument, shell history, issue, commit, or chat):

```bash
read -rsp "Prove2me API key: " PROVE2ME_API_KEY; echo
export PROVE2ME_API_KEY

python3 -m semantic_graph.publish \
  --theorem-name BitcoinSupply.supply_lt_maxMoney \
  --explanation-file contributions/bitcoin_supply_lt_maxMoney_explanation.md
```

This **reads** the exact theorem record, scans your own submissions, and verifies the current accepted submission is accessible. It shows the discovered theorem/submission IDs and hashes of the current and proposed explanations, **without modifying Prove2me**. It refuses to select among multiple owned accepted submissions without `--submission-id`.

If there is already a nonempty published explanation, the command refuses to replace it. Decide whether to preserve the existing explanation, improve it manually, or explicitly use `--replace-existing` to overwrite it.

## Submit only after reviewing the preview

Use the **exact submission ID printed by the preview**:

```bash
python3 -m semantic_graph.publish \
  --theorem-name BitcoinSupply.supply_lt_maxMoney \
  --explanation-file contributions/bitcoin_supply_lt_maxMoney_explanation.md \
  --apply \
  --confirm-submission-id YOUR_EXACT_SUBMISSION_UUID
```

If the existing explanation is nonempty, add `--replace-existing` after reviewing what will be replaced. If there are multiple accepted submissions for the theorem under your account, also add `--submission-id YOUR_EXACT_SUBMISSION_UUID` to both commands.

When finished:

```bash
unset PROVE2ME_API_KEY
```

The tool permits only a single `PATCH` for the creator-owned submission's `explanation`; it cannot submit proofs, create theorems, change verification status, alter other users' submissions, or contact researchers. API ownership and authorization are ultimately enforced by Prove2me.

## Safety guarantees and limits

- API key exchanged for a short-lived token in memory; no keys embedded in source or fixtures.
- Account submission list is used to establish owner membership before any write.
- Exact theorem name and theorem ID are matched; no fuzzy mapping.
- Only `ACCEPTED` or `SKETCH_ACCEPTED` submissions can be selected.
- Default is preview only; `--apply` and `--confirm-submission-id` are required to change anything.
- Existing prose is never overwritten without `--replace-existing`.
- Authenticated redirects are disabled; the API endpoint hostname is fixed to `prove2.me`.
- This is **not a proof of correctness** of the mathematical explanation.
- No API endpoint exists in the documented interface for installing the semantic graph backend/frontend; a platform code contribution would be a separate repository change.

**If an API key was ever pasted into a chat or otherwise exposed outside your password manager or local environment, revoke it and obtain a new key before running this workflow.**
