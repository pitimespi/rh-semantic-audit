# Publication and engagement policy

## Status

This repository was created by the owner and is being populated with the standalone audit. No upstream outreach is authorized.

**Do not:** open issues or pull requests in other repositories, comment on anyone else's research, contact Alpöge or verification maintainers, post announcements, or imply independent mathematical verification. The repository can be public without engaging the community, per the project owner's current instruction.

## Repository setup (completed)

Create `pitimespi/rh-semantic-audit` using GitHub's New Repository page. Public visibility was the intended choice in the project plan, but the owner can choose private until ready. Do **not** initialize the GitHub repository with README, `.gitignore`, or LICENSE: these are present in the starter files.

With these files extracted into a local `rh-semantic-audit/` directory:

```sh
cd rh-semantic-audit
git init -b main
git add .
git commit -m "Initial source-linked RH semantic audit (v0.2)"
git remote add origin https://github.com/pitimespi/rh-semantic-audit.git
git push -u origin main
```

You can instead connect this new repository to ChatGPT and request publication of the prepared files there. No GitHub credentials or tokens are included in this package.

## Pre-publication checks

- [x] Include only original reports, script, graph metadata and synthetic unit-test content.
- [x] Pin the mirror revision and cite existing related research.
- [x] Separate source-text findings from proof-term checking and mathematical validity.
- [x] State the engagement hold clearly.
- [x] Supply a reproducible standard-library Python scanner and tests.
- [x] Create the `pitimespi/rh-semantic-audit` repository.
- [ ] Verify all prepared files are uploaded.
- [ ] Verify the GitHub remote shows the intended README, audit files and provenance.

## What to do later, only when authorized

After a mathematical specialist reviews the expanded literature/theta interface, consider a concise public issue referencing the new repository. No such outreach is authorized by the current instruction.