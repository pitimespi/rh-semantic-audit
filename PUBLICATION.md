# Publication and engagement policy

## Status

The reusable research prototype (v0.5) is published in the owner's standalone repository:
https://github.com/pitimespi/rh-semantic-audit

The initial release contained 12 files. Version 0.3 added the `semantic_graph/` engine. Version 0.4 added read-only Prove2me adapter logic and the local proposal-item provenance; version 0.5 adds source-line-verified Bitcoin semantic explanations and a local interactive graph viewer. CI checks Python tests, fixture validation, JavaScript syntax, and pinned Bitcoin source references. The original reports and scanner remain available.

**No community engagement is authorized.** Do not open issues or pull requests in other repositories, comment on others' research, contact Alpöge or verification maintainers, or post announcements without new explicit authorization.

## Release checks

- [x] Create `pitimespi/rh-semantic-audit`.
- [x] Publish the initial reports and the new semantic proof graph engine under `main`.
- [x] Preserve exact source version pins and provide links to related research.
- [x] Include only original audit text, scanner and synthetic tests; do not redistribute the author's unlicensed Lean source.
- [x] State limits: source-text inspection is not mathematical proof or independent kernel replay.
- [x] Verify the repository tree contains the intended files.\n- [x] Verify the semantic graph CI checks completed successfully, including the pinned Bitcoin source checks and the interactive viewer syntax (GitHub Actions run 44848731009).
- [x] Keep the original `pitimespi/prove2me` repository unchanged.
- [x] Do not engage upstream maintainers or researchers.

## Research next steps (internal)

1. Obtain a platform-supported theorem-ID/dependency export from Prove2me before calling these true kernel dependencies; currently the Bitcoin example records imports as candidates.\n2. Expand `OpenLiteratureStatements` into a field-by-field mathematical read-back.
3. Extract the exact elaborated type and prerequisites of `every_character_of_theta_integrals_local_matching`.
4. Produce independent interpretations and flag differences as explicit review questions.
5. Only with permission, consider proposing individual findings upstream.

The standalone GitHub repository being public does not imply outreach, endorsement, or independent validation of Alpöge's claimed proof.
