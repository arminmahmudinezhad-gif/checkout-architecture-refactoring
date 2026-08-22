---
name: solid-refactoring
description: SOLID violation analysis and evidence collection. Use when reviewing object-oriented code for SRP, OCP, LSP, ISP, or DIP before planning a refactor.
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
