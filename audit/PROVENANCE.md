# Provenance and trust boundaries

**Checked on 2026-11-20** against the connected GitHub repository and public verification documentation. Pin hashes below to reproduce the same source-level review.

| Artifact | Identifier | Interpretation |
|---|---|---|
| Original announcement | `https://alpo.ge/remark.pdf` | Author's claim and outline, not itself a complete proof |
| Announcement PDF SHA-256 (reported in verification mirror) | `3fc97784b71ddd44ff8aa0a177e99622a1c61b13cfa843a0989ee4a7a0cfeb8d` | Verify if obtaining the PDF |
| Original multipart archive, joined SHA-256 (reported by mirror) | `9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc` | Verify if downloading 14 parts |
| GitHub verification mirror | `Deicyde/riemann-hypothesis` | Third-party mirror with supplemental verification assets |
| **Mirror commit audited** | `e50d09817ad81469f737e8f637561e6ccf86c670` | Exact tree baseline for our source navigation |
| Mathlib revision | `0df444a360eaa60ab8c11dca51a86af692955474` | From the mirror's `lake-manifest.json` |
| Lean toolchain | `leanprover/lean4:v4.33.1` | From mirror documentation |
| Original tree marker | `40e56bab` (first mirror commit, as reported) | Mirror says this preserves original published archive |

The archive hashes were **read from the mirror's verification notes, not recomputed by us**. We did directly retrieve the mirror HEAD SHA via GitHub and read selected files from the pinned commit.

References:
- [Mirror verification notes](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/verification/NOTES.md)
- [Mirror README](https://github.com/Deicyde/riemann-hypothesis/blob/e50d09817ad81469f737e8f637561e6ccf86c670/README.md)
- [MIT verifier updates](https://math.mit.edu/~drew/grh/)

## Scope boundaries

1. **Compilation != complete independent trust.** The verification mirror reports that some tactics directly assign terms to goals, leaving kernel checks especially important. Independent proof-term replay and statement comparison are different from a local `lake build`.
2. **Top-level statement checking != human mathematical explanation.** The headline theorem invokes Mathlib's `RiemannHypothesis`, and the independent challenge lists the five statements. The upstream argument remains conceptually hard to understand.
3. **Source-text indexing != Lean elaboration.** Our script detects textual occurrences, not hidden implicit arguments, elaborated constants, or kernel dependencies.
4. **Auditing != endorsement.** Even multiple accepting checker reports are evidence to assess, not a substitute for professional review and acceptance of an extraordinary result.
5. **Copyright:** The submitted Lean source is noted as lacking an explicit reuse license. This package redistributes none of it.
