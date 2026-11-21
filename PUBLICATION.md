# RH semantic audit — publication and scope policy

**Version 0.8 (2026-11-20)** · Active scope: **Riemann Hypothesis only**.

Repository: https://github.com/pitimespi/rh-semantic-audit

## Status

- [x] Publish an RH-only research introduction and roadmap in [README.md](README.md).
- [x] Preserve pinned provenance for third-party source mirror commit `e50d09817ad81469f737e8f637561e6ccf86c670`.
- [x] Document the exact three fields of `OpenLiteratureStatements` and their source-level construction in [AUDIT-003](audit/AUDIT-003-OPEN-LITERATURE.md).
- [x] Enrich the [RH semantic graph](examples/rh_critical_path.json) with those explicit assumptions.
- [x] Make the [viewer](viewer/index.html) show RH as the sole example choice.
- [x] Add an RH-only source-text checker that reads selected files by immutable Git commit, without distributing or executing unlicensed Lean source.
- [x] Confirm GitHub Actions [RH-only workflow](https://github.com/pitimespi/rh-semantic-audit/actions/runs/44850737317) passed 48 unit tests, graph validation, JavaScript syntax, and pinned RH source interface checks.
- [x] Preserve older unrelated engineering examples as [inactive legacy material](docs/LEGACY.md) rather than deleting them without a specific request.
- [x] Maintain the hold on outreach: no issues, PRs, public comments, researcher contacts or upstream submissions.

## Limits and next steps

The new field inventory and CI check are *source-level results*. They do not demonstrate the mathematical correctness of the published RH claim, expand implied arguments or instances, check for axioms, reconstruct an elaborated dependency graph, or replay the proof in the Lean kernel.

**Next checks:** expand `UpperTheory.One.M.Row` versus `UpperTheory.GalStar.Row0b`, analyze the `recTExists` theorem's prerequisites, and retrieve a precise elaborated type and independent mathematical read-back of `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`.

The Prove2me integration and Bitcoin files are historical scaffolding only. **No Prove2me theorem or explanation has been submitted** as part of this RH audit. The RH source in the mirror has no explicit reuse license reported; no original proof source is redistributed in this project.

A previously exposed Prove2me API key should be revoked and replaced; no credential belongs in GitHub commits or automation.
