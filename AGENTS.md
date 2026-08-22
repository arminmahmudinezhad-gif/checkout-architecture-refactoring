# Project Instructions

## Objective

This repository is a two-person Software Engineering Laboratory assignment and
a portfolio case study. It compares the effort required to add cash payment to
an initial checkout system before and after applying SOLID principles.

The required workflow is:

1. Preserve the initial design in `01-Without-OOD-Principles`.
2. Add cash payment to that version without refactoring it.
3. Record every effective change and analyze all five SOLID principles.
4. Create an OpenCode Skill that detects violations, explains evidence,
   proposes refactoring, and edits only after user approval.
5. Produce and review a refactoring Plan.
6. Create `02-Applied-OOD-Principles` and apply the approved refactoring there.
7. Add cash payment again to the refactored version.
8. Compare the change effort in both versions and evaluate OpenCode.
9. Keep the complete report in the root `README.md`.

The assignment PDF is authoritative when it is available to the session.

## Team And Commit Rules

- Armin Mahmudinezhad and Soroush Pournasiri must each author exactly 10
  meaningful commits.
- Armin works on `armin/work`; Soroush works on `soroush/work`.
- The user creates commits and pushes manually. Never run `git commit`, amend,
  or push unless explicitly requested.
- Synchronize completed work with `git merge --ff-only`; do not create extra
  merge commits for branch handoffs.
- Before any work, inspect `git status`, the recent log, and both remote
  branches. Git history is the source of truth if this checklist is stale.
- Preserve other contributors' work and authorship.
- After every Armin task, state Soroush's exact next task, files, verification,
  commit message, and synchronization point.

## Immutable Initial Version

Do not refactor `01-Without-OOD-Principles`. It intentionally demonstrates the
cost of extending the original design. Later architectural changes belong only
in `02-Applied-OOD-Principles`.

Run its checks from that directory:

```powershell
python -m unittest discover -s tests -v
python -m store.main
```

## Commit Plan And Progress

Completed commits must be confirmed from `git log`, not assumed solely from
this list.

### Armin

- [x] A1 `chore: prepare initial project snapshot`
- [x] A2 `feat(without-solid): add core cash payment logic`
- [x] A3 `test(without-solid): add cash payment unit tests`
- [x] A4 `docs: record initial implementation changes`
- [x] A5 `docs: analyze SRP OCP and DIP violations`
- [x] A6 `feat(skill): add SOLID detection and evidence workflow`
- [x] A7 `docs(plan): propose SOLID refactoring plan`
- [ ] A8 `refactor: introduce payment abstractions`
- [ ] A9 `feat(applied): implement cash payment extension`
- [ ] A10 `docs: compare initial and refactored implementations`

### Soroush

- [x] S1 `test: characterize existing payment behavior`
- [x] S2 `feat(without-solid): integrate cash into payment flow`
- [x] S3 `test(without-solid): add cash payment integration tests`
- [x] S4 `docs: justify initial changes and record prompts`
- [x] S5 `docs: analyze LSP ISP and architecture dependencies`
- [x] S6 `feat(skill): add refactoring and user approval workflow`
- [ ] S7 `docs(plan): review and refine refactoring plan`
- [ ] S8 `refactor: migrate implementations and decouple dependencies`
- [ ] S9 `test(applied): add cash and regression test coverage`
- [ ] S10 `docs: evaluate OpenCode and finalize experiment report`

## Current Handoff

Soroush S6 is complete. Armin A7 prepares
`02-Applied-OOD-Principles/REFACTORING_PLAN.md` and introduces this
`AGENTS.md`; both files belong to the same A7 commit. After A7 is committed and
pushed, Soroush must perform S7 by reviewing and refining the proposed plan and
documenting the reasons for each correction. Do not apply the refactoring until
S7 is complete and approved.

## Working Expectations

- Analyze the repository before editing and make the smallest correct change.
- Keep the initial and applied versions independently runnable.
- Use evidence with file and symbol references for SOLID findings.
- Run relevant tests after code changes and report failures honestly.
- Do not invent completed prompts, reviews, test results, or OpenCode behavior.
- Keep README measurements reproducible from Git diffs.
