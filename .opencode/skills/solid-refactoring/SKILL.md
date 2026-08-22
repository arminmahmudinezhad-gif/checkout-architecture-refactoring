---
name: solid-refactoring
description: SOLID violation analysis, evidence collection, and step-by-step refactoring with user approval gates. Use when reviewing object-oriented code for SRP, OCP, LSP, ISP, or DIP, or when planning or applying a refactor to address those violations.
---

# SOLID Refactoring

Analyze the current implementation before suggesting or making changes. Treat
SOLID principles as design heuristics, not rules that every class must satisfy
in the same way.

## Analysis Workflow

1. Establish the review scope and identify the command that runs the existing
   tests or application.
2. Read the relevant production code and tests before judging the design.
3. Map the important classes, their responsibilities, inheritance
   relationships, and concrete dependencies.
4. Evaluate each SOLID principle independently using the checks below.
5. Report only findings supported by a concrete code location and an observable
   maintenance or substitution risk.
6. Present the analysis and wait for the user before planning or applying any
   refactoring.

Do not edit files during this analysis phase.

## Detection Checks

### SRP: Single Responsibility Principle

Look for a class or function with multiple independent reasons to change, such
as mixing business policy, persistence, external communication, validation, or
presentation. A long method alone is not sufficient evidence; identify the
distinct stakeholders or change triggers.

### OCP: Open/Closed Principle

Look for stable code that must be edited whenever a new variant is introduced.
Common signals include type or string dispatch chains, repeated conditionals,
and central classes that enumerate every implementation. Confirm the issue by
describing the exact edits required for one realistic extension.

### LSP: Liskov Substitution Principle

Inspect inheritance and implementation contracts. Look for subtypes that reject
valid parent operations, strengthen preconditions, weaken postconditions,
return incompatible results, or introduce unexpected exceptions. State the
client expectation that substitution would break.

### ISP: Interface Segregation Principle

Look for consumers or implementations forced to depend on operations they do
not use or cannot support. Empty methods and `NotImplementedError` in an
implementation are strong signals, but verify that the operations belong to
separate client roles.

### DIP: Dependency Inversion Principle

Look for high-level policy that imports, constructs, or controls concrete
infrastructure and volatile implementations. Record both the dependency and
its construction point. Depending on a concrete value object is not by itself
a DIP violation.

## Evidence Standard

Every reported violation must include:

- the principle;
- the file and symbol where it occurs;
- the relevant behavior or dependency;
- why it violates the principle;
- a realistic change that exposes the design cost;
- the confidence level: high, medium, or low.

Do not report a principle merely because an abstraction could be added. Mark a
principle as respected or not applicable when no concrete violation is found.

## Analysis Output

Start with this summary table:

| Principle | Status | Location | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| SRP | Respected / Violated / N/A | `path:symbol` | Concise evidence | High / Medium / Low |
| OCP | Respected / Violated / N/A | `path:symbol` | Concise evidence | High / Medium / Low |
| LSP | Respected / Violated / N/A | `path:symbol` | Concise evidence | High / Medium / Low |
| ISP | Respected / Violated / N/A | `path:symbol` | Concise evidence | High / Medium / Low |
| DIP | Respected / Violated / N/A | `path:symbol` | Concise evidence | High / Medium / Low |

Follow the table with one evidence section per violation. Separate confirmed
violations from uncertain design concerns, and state any assumptions or test
gaps that limit the analysis.

## OpenCode Modes

Use **Plan mode** to analyze violations, propose the refactoring sequence,
identify affected files, and define verification without editing application
code. Present that plan for review and explicit user approval.

Switch to **Build mode** only after approval. Apply the reviewed plan in small
steps, preserve unrelated work, and run the agreed verification after each
step.

## Refactoring Workflow

Apply the refactoring only after the analysis has been presented and the user
has approved proceeding. Work in small, behavior-preserving steps:

1. Inspect the current tests that cover the code being changed before editing
   anything. Run the existing test command to establish a green baseline.
2. Prefer the smallest change that addresses the reported violation. Create the
   abstraction or collaborators called for in the analysis, then rewire the
   consumers with constructor or method-level injection.
3. Move one dependency or responsibility at a time. After each move, run the
   test suite and fix regressions before continuing.
4. Verify the solution by re-running the relevant tests and the application
   entry point when one exists.
5. Do not interrupt the refactor to address a new principle; record it as a
   follow-up and finish the current step first.

Do not combine unrelated refactorings into the same change set.

## User Approval Workflow

Every refactor passes through explicit user approval gates. Before making any
change, confirm the step using the question tool and wait for the user's
response before continuing:

1. Confirm the refactoring plan (scope, order of steps, affected files) and any
   commits that will be produced, including commit messages.
2. Before editing a file, confirm the specific change if more than one
   reasonable approach exists.
3. Before running tests or the application, confirm the verification command
   when a choice is available.
4. Before committing or pushing, confirm the commit was requested and review
   the exact staging command.

Never skip a gate, assume approval, or continue past a rejected step. When the
user rejects a suggestion, record the correction and adapt the plan.
