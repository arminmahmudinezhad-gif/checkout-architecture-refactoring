# Checkout Architecture Refactoring

A case study comparing the effort required to extend an initial checkout system
before and after applying SOLID design principles.

## Contributors

- Armin Mahmudinezhad
- Soroush Pournasiri

## Step 1: Add Cash Payment to the Initial Design

The original project was preserved in `01-Without-OOD-Principles`. Cash payment
was added to this version without refactoring its existing design.

### Baseline Verification

The unmodified application was run successfully before implementing the new
payment method. The initial credit-card and bundle checkout scenarios both
completed without errors.

### Change Inventory

| Row | Class or file | Change type | Change description |
| ---: | --- | --- | --- |
| 1 | `store/payment.py` (`PaymentProcessor.process`) | Conditional branch added | Added a `cash` case to the existing payment-method chain, including its console message and `paid_by_cash` receipt value. |
| 2 | `store/main.py` (`build_demo_orders`, `main`) | Demo data and checkout flow changed | Added a cash order, returned it from the demo builder, and processed it through `OrderService`. |
| 3 | `tests/test_payment.py` | Test file added | Added focused unit coverage for the cash branch's receipt and console message. |
| 4 | `tests/test_existing_payments.py` | Test file added | Characterized credit-card, PayPal, Bitcoin, and unsupported-method behavior before further changes. |
| 5 | `tests/test_cash_checkout.py` | Test file added | Added integration coverage for cash checkout status and receipt output through `OrderService`. |

Paths in the table are relative to `01-Without-OOD-Principles`.

### Change Measurements

| Scope | Files changed | Lines added | Lines removed |
| --- | ---: | ---: | ---: |
| Production code | 2 | 15 | 2 |
| Test code | 3 | 133 | 0 |
| Total | 5 | 148 | 2 |

These measurements use the preserved initial snapshot as the comparison base.

### Why Each Change Was Necessary

| Row | Change | Why it was necessary |
| ---: | --- | --- |
| 1 | `store/payment.py` cash branch | Cash is a distinct checkout path with its own receipt token (`paid_by_cash`) and console message; the processor must recognize `"cash"` or every cash order fails with `Unknown payment method`. |
| 2 | `store/main.py` demo flow | The demo previously proved only credit-card and bundle scenarios; cash needed a realistic order (with at least one `OrderItem`), returned from `build_demo_orders()` and processed in `main()`, so the feature is exercised end to end. |
| 3 | `tests/test_payment.py` | A focused unit test pins the cash branch: its receipt value and console message. |
| 4 | `tests/test_existing_payments.py` | Characterized the pre-cash methods (credit card, PayPal, Bitcoin, unknown) so later changes cannot silently alter behavior that other flows still depend on. |
| 5 | `tests/test_cash_checkout.py` | Proves the full `OrderService` flow for cash (status `"paid"` and receipt in output), which the unit test on `PaymentProcessor` alone cannot guarantee. |

Paths in the table are relative to `01-Without-OOD-Principles`.

### Why the Existing Conditional Structure Had to Be Modified for Cash

`PaymentProcessor.process` dispatches on `order.payment_method` through an
`if`/`elif` chain. The structure is closed to unknown methods but *open to
modification*: every payment method must be added as a new branch.

Cash required exactly one more branch, but the chain made this non-obvious:

- The receipt token is derived from the branch name (`paid_by_cash`), so a
  missing branch silently leaves cash customers unable to pay.
- The `else` branch would otherwise raise `Unknown payment method: 'cash'`,
  aborting a valid order at charge time.
- Because the decision is driven by a string method name, there is no way to
  register a new method without editing the existing chain — the reason the
  structure is a later refactoring target.

Adding the `cash` branch was the minimal change that kept behavior consistent
with the other methods.

### Why Unit, Characterization, and Integration Tests Were Needed

Each layer covers a different risk:

- **Unit** (Armin's `test_payment.py`): isolates the cash branch of
  `PaymentProcessor` — verifies the `paid_by_cash` receipt and the
  `[payment] Accepting cash` message in isolation.
- **Characterization** (`test_existing_payments.py`): captures the current
  behavior of credit-card, PayPal, Bitcoin, and unsupported-method paths before
  the demo flow changed. These tests are the safety net that shows a regression
  in any pre-existing method.
- **Integration** (`test_cash_checkout.py`): drives the whole
  `OrderService.process_order` pipeline for a cash order — validations, pricing,
  payment, persistence, notification, and receipt printing — and verifies the
  order ends up `"paid"` with `paid_by_cash` in the output. External services
  are avoided by patching the print side effects.

The unit test proves the branch; the integration test proves the flow.

### OpenCode Prompts Used During Step 1

1. "Add characterization tests for payment methods that already existed before
   cash: Credit card, PayPal, Bitcoin, Unknown payment method," creating
   `tests/test_existing_payments.py` with `unittest`, without changing
   production code.
2. "Integrate cash payment into the demonstration checkout flow," modifying
   `store/main.py` to build a realistic cash order, return it from
   `build_demo_orders()`, and process it through `OrderService`, without
   touching `payment.py` or refactoring for SOLID.
3. "Add an integration test for cash checkout through `OrderService`,"
   creating `tests/test_cash_checkout.py` that verifies order status `"paid"`
   and the cash receipt in checkout output, mocking out external side effects
   and avoiding duplication of Armin's unit test.

### OpenCode Suggestions: Accepted, Corrected, Rejected

**Accepted**

- Characterizing the pre-cash payment methods before changing the demo flow.
- Patching console output with `unittest.mock.patch` in the integration test so
  no real external service is contacted.
- Covering the full `OrderService` flow for the new cash tests rather than only
  `PaymentProcessor`.
- Keeping `store/payment.py` untouched because the cash branch already existed.

**Corrected**

- The documented verification commands consistently retain `python -m unittest
  ...`; no environment-specific `python3` correction is claimed.
- The initial integration-test drafts overlapped with Armin's `PaymentProcessor`
  unit test; they were reworked to drive `OrderService` end to end and assert on
  status and receipt output instead.

**Rejected**

- Refactoring `PaymentProcessor` or other classes, and applying SOLID
  principles during Step 1 — explicitly deferred to the later steps of the
  case study.

## Step 2: SOLID Design Analysis

The initial implementation was reviewed before any architectural refactoring.
This section records the observed violations, their locations, and the proposed
corrections.

### SOLID Assessment

| Principle | Respected? | Location | Summary |
| --- | --- | --- | --- |
| SRP | No | `store/order_service.py`, `OrderService` | The service validates orders, calculates totals and shipping, processes payment, persists data, sends notifications, and prints receipts. |
| OCP | No | `store/payment.py`, `PaymentProcessor.process`; `store/pricing.py`, `DiscountCalculator.calculate` | Adding a payment method or discount rule requires modifying an existing conditional chain. |
| LSP | No | `store/notification.py`, `SmsOnlyNotifier` | The subtype rejects inherited email and push operations by raising `NotImplementedError`, so it cannot safely replace `NotificationService`. |
| ISP | No | `store/notification.py`, `NotificationService` | Clients and subtypes are forced to depend on email, SMS, and push operations even when they support only one channel. |
| DIP | No | `store/order_service.py`, `OrderService.__init__` | The high-level checkout workflow constructs and depends directly on concrete payment, notification, pricing, and database classes. |

Paths in this analysis are relative to `01-Without-OOD-Principles`.

### SRP: Single Responsibility Principle

**Violation location:** `store/order_service.py`, particularly
`OrderService.process_order` and `_print_receipt`.

**Cause of violation:** `OrderService` has several independent reasons to
change. It contains order validation rules, shipping and total calculation,
payment orchestration, persistence, notification-channel selection, and receipt
formatting. A change to receipt presentation or storage technology therefore
requires editing the same class that controls the checkout use case.

**Proposed refactoring:** Keep `OrderService` as the checkout orchestrator, but
move validation, total calculation, receipt formatting, persistence, and
notification behavior behind focused collaborators. The service should
coordinate these operations instead of implementing them directly.

**Reason for this approach:** The workflow remains visible in one application
service, while each implementation detail gets a separate reason to change.
This reduces the risk that a presentation or infrastructure change alters the
checkout policy.

### OCP: Open/Closed Principle

**Violation locations:**

- `store/payment.py`, where `PaymentProcessor.process` selects payment behavior
  through an `if`/`elif` chain.
- `store/pricing.py`, where `DiscountCalculator.calculate` selects discount
  rules through another conditional chain.

**Cause of violation:** Every new payment method requires another branch in
`PaymentProcessor`. Adding cash demonstrated this directly: the existing class
had to be edited before a cash order could be processed. Discount rules have the
same problem because every new rule changes `DiscountCalculator`.

**Proposed refactoring:** Represent payment methods and discount rules as
separate implementations of stable abstractions. Select payment handlers by
method name and evaluate injected discount policies without modifying the
checkout workflow.

**Reason for this approach:** New behavior can be introduced by adding a new
implementation and registering or injecting it. Existing, tested implementations
remain closed to modification, while the system remains open to extension.

### LSP: Liskov Substitution Principle

**Violation location:** `store/notification.py`, where `SmsOnlyNotifier`
inherits from `NotificationService`.

**Cause of violation:** `NotificationService` establishes that its instances
can send email, SMS, and push notifications. `SmsOnlyNotifier` inherits that
contract but raises `NotImplementedError` for `send_email` and `send_push`. A
client that works with `NotificationService` can therefore fail when an
`SmsOnlyNotifier` is substituted, even though it is declared as a subtype.

**Proposed refactoring:** Remove the inheritance relationship between
`SmsOnlyNotifier` and the multi-channel service. Introduce channel-specific
notifier implementations that share a small notification abstraction, such as
a single `send` operation. The checkout workflow can receive a collection of
notifiers and invoke the same supported operation on each one.

**Reason for this approach:** Every notifier will satisfy the complete contract
it advertises. Email, SMS, and push implementations can then be substituted
without introducing unsupported operations or changing expected client
behavior.

### ISP: Interface Segregation Principle

**Violation location:** `store/notification.py`, particularly the combined
email, SMS, and push operations exposed by `NotificationService`.

**Cause of violation:** The notification contract groups three independent
delivery channels. A notifier that supports only SMS is still forced to inherit
email and push methods, which leads to placeholder implementations that throw
exceptions.

**Proposed refactoring:** Replace the broad channel-specific contract with a
small `Notifier` abstraction containing one `send(customer, message)` operation.
Provide separate `EmailNotifier`, `SmsNotifier`, and `PushNotifier`
implementations. Consumers should depend only on the notifier instances they
actually use.

**Reason for this approach:** The smaller contract removes unsupported methods,
allows channels to evolve independently, and lets the checkout service add or
remove notification channels without requiring changes to unrelated notifier
classes.

### DIP: Dependency Inversion Principle

**Violation location:** `store/order_service.py`, particularly
`OrderService.__init__`.

**Cause of violation:** The high-level checkout policy directly imports and
constructs `DiscountCalculator`, `PaymentProcessor`, `NotificationService`, and
`MySqlDatabase`. It therefore depends on concrete implementation details and
cannot replace them without editing `OrderService`.

**Proposed refactoring:** Define small abstractions for pricing, payment,
persistence, notification, and receipt output. Supply their implementations to
`OrderService` through constructor injection. Create concrete dependencies only
in the application composition root.

**Reason for this approach:** The checkout workflow will depend on contracts
rather than infrastructure details. Constructor injection also makes behavior
replaceable and allows tests to use controlled collaborators without patching
internals.

### Current Concrete Dependency Map

Before refactoring, the high-level checkout workflow has these direct
dependencies:

```text
OrderService
|-- DiscountCalculator
|-- PaymentProcessor
|-- NotificationService
`-- MySqlDatabase

PaymentProcessor
`-- Order and Customer payment fields

DiscountCalculator
`-- Order pricing, coupon, item-count, and customer VIP fields

SmsOnlyNotifier
`-- NotificationService inheritance
```

`OrderService.__init__` constructs all four concrete collaborators itself.
`OrderService.process_order` also chooses email and SMS operations directly.
These dependencies couple the checkout policy to infrastructure and
channel-specific behavior, supporting the SRP, OCP, ISP, and DIP findings above.

### Verification

Run the initial version and its tests from the repository root:

```powershell
cd 01-Without-OOD-Principles
python -m unittest discover -s tests -v
python -m store.main
```

All seven tests pass, and the demo completes the credit-card, bundle, and cash
checkout scenarios.

## Step 3: Create the OpenCode SOLID Refactoring Skill

The project-scoped Skill is stored at
`.opencode/skills/solid-refactoring/SKILL.md`. Armin's A6 added detection checks
for all five principles, evidence requirements, confidence levels, and a
structured findings format. Soroush's S6 added incremental refactoring guidance,
explicit user-approval gates, rejection handling, verification steps, and a
rule against unrelated refactoring.

The Skill separates analysis from implementation: it first reports concrete
violations and risks, then proposes scoped changes, and edits only after the
user approves the reviewed plan.

## Step 4: Refactoring Plan Review (S7)

Armin's A7 proposed `02-Applied-OOD-Principles/REFACTORING_PLAN.md`. Soroush
reviewed it against the five SOLID violations from Step 2 and refined it in
the same file. The repository records the reviewed plan and its implementation
in A8/S8; it does not establish a separate historical approval interaction.

The plan documents the scope, affected files, implementation order, risks, and
verification commands, and Soroush reviewed and corrected it before
implementation. The repository does not establish that A7/S7 used an
explicitly selected OpenCode Plan agent.

### Accepted Plan Suggestions

- The five-phase structure was kept because it maps one-to-one onto the
  documented violations: payment abstractions (payment OCP), workflow
  decoupling (SRP, discount OCP, LSP, ISP, DIP), cash as a pure extension, and
  a final verification phase.
- Keeping `OrderService` as the orchestrator while moving validation and
  receipt printing behind focused collaborators.
- Using a single `contracts.py` for the remaining structural contracts instead
  of one file per contract.
- Constructor injection with the concrete construction confined to
  `store/main.py` as the composition root.
- Stating that cash must be absent before Phase 3 (Armin's A9) so the added
  and refactored versions stay comparable.

### Corrected Plan Suggestions

- The baseline commit was confirmed with git evidence as `6908c62`
  (no `cash` branch in `payment.py`, no cash order in `main.py` at that
  revision), and Phase 0 was changed to copy from the git tree at that commit
  (`git archive 6908c62 store`) rather than from the current
  `01-Without-OOD-Principles`, which already contains cash.
- A8/S8 file ownership was not explicit enough to prevent overlapping edits;
  a phase-by-owner file table was added so Armin and Soroush never edit the
  same files in the same phase window.
- The verification commands consistently retain the tested `python` commands;
  no environment-specific `python3` requirement applies.

### Rejected Plan Suggestions

- A dedicated receipt-formatting contract was rejected. The receipt printer
  has a single implementation and one public method, so a separate protocol
  would be an abstraction without a consumer.
- A push notification implementation was rejected. The checkout workflow never
  sends push, so implementing `PushNotifier` would reproduce the unused
  operations that created the original ISP violation.
- Separate handler/rule directories were rejected in favor of keeping handlers,
  notifiers, and discount rules in the modules they belong to
  (`payment.py`, `notification.py`, `pricing.py`).

### Revisions In `02-Applied-OOD-Principles/REFACTORING_PLAN.md`

Additionally, the plan status was revised to record that Phases 0-4 were
implemented and verified. A violation-to-correction mapping table, an
abstraction-simplification section, and a file-ownership table were added, and
the acceptance criteria include the requirement that no cash logic exists in
the applied folder before Phase 3.

## Step 5: Apply the Reviewed SOLID Refactoring

The applied version was created from the pre-cash tree at commit `6908c62`, so
cash could be introduced later as a separate, measurable extension. The two
versions remain independently runnable and do not import from each other.

The reviewed refactoring was applied incrementally through A8 and S8, with the
tests and application executed after each phase. The repository does not
establish that A8/S8 used an explicitly selected OpenCode Build agent.

### Resulting Design

| Principle | Applied correction | Evidence in `02-Applied-OOD-Principles` |
| --- | --- | --- |
| SRP | Improved: validation, discounts, payment, persistence, notification delivery, and receipt output are delegated. `OrderService` retains use-case calculations, status transition, and message construction. | `store/order_service.py`, `store/validation.py`, `store/receipt.py` |
| OCP | Payment methods use registered handlers, and discounts use an ordered collection of rule objects. | `store/payment.py`, `store/pricing.py` |
| LSP | The invalid `SmsOnlyNotifier` subtype was removed; each notifier implements its complete contract. | `store/notification.py` |
| ISP | Email and SMS implementations expose only the shared `send` operation used by checkout. | `store/contracts.py`, `store/notification.py` |
| DIP | `OrderService` receives its collaborators through constructor injection; concrete construction is in the composition root. | `store/order_service.py`, `store/main.py` |

Armin's A8 introduced the payment extension point and migrated credit card,
PayPal, and Bitcoin without adding cash. Soroush's S8 then migrated the other
responsibilities and moved concrete dependency wiring to `store/main.py`.

## Step 6: Add Cash to the Refactored Design

Cash was added only after the refactoring was complete. The extension added a
`CashPaymentHandler`, registered it in the composition root, and added a cash
order to the demonstration flow. It did not modify `PaymentProcessor`, any
existing payment handler, or `OrderService`.

### Applied-Version Change Inventory

| Row | Class or file | Change type | Change description |
| ---: | --- | --- | --- |
| 1 | `store/payment.py` (`CashPaymentHandler`) | Class added | Encapsulated the cash console message and `paid_by_cash` receipt token in a new handler. |
| 2 | `store/main.py` (`build_payment_processor`) | Registration added | Registered `CashPaymentHandler` alongside the existing handlers. |
| 3 | `store/main.py` (`build_demo_orders`, `main`) | Demo data and flow changed | Added and processed the same realistic cash scenario used in the initial version. |
| 4 | `tests/test_cash_checkout.py` | Test file added | Added focused handler checks and checkout integration coverage without changing production code. |

Paths in this section are relative to `02-Applied-OOD-Principles`.

## Step 7: Compare Initial and Refactored Extensions

### Reproducible Measurements

The initial-version range starts at the preserved pre-cash snapshot and ends
after its cash production and test work. The applied-version range starts after
the reviewed refactoring and ends after cash tests:

```powershell
git diff --numstat bf7a03b..ca2e90e -- 01-Without-OOD-Principles
git diff --numstat 1ff96dc..231e2e0 -- 02-Applied-OOD-Principles
```

| Version and scope | Files changed | Lines added | Lines removed |
| --- | ---: | ---: | ---: |
| Initial production | 2 | 15 | 2 |
| Initial tests | 3 | 133 | 0 |
| Initial total | 5 | 148 | 2 |
| Applied production | 2 | 22 | 3 |
| Applied tests | 1 | 65 | 0 |
| Applied total | 3 | 87 | 3 |

The applied production change has more added lines because a complete handler
class makes the behavior explicit, while the initial version added a smaller
conditional branch. Raw line count therefore does not by itself show design
quality. The important change-effort difference is where those lines went.

### Change-Effort Comparison

| Question | Initial design | Applied SOLID design |
| --- | --- | --- |
| Was central payment dispatch modified? | Yes; `PaymentProcessor.process` gained another `elif` branch. | No; registry dispatch was unchanged. |
| Were existing payment implementations modified? | Payment variants were branches in the modified processor. | No; all three existing handler classes were unchanged. |
| Was checkout orchestration modified? | No. | No. |
| Where was the new behavior implemented? | Inside an existing conditional chain. | In one new `CashPaymentHandler`. |
| How was the method enabled? | By changing the processor's method-selection logic. | By registering the new handler in the composition root. |
| Test changes in the measured range | Three files and 133 lines: 70 characterize pre-existing methods and 63 directly test cash. | One new 65-line cash test file because pre-cash regression coverage already existed. |

The initial version required changing stable dispatch logic, so every future
payment method would increase the same conditional chain and its regression
risk. The applied version still required explicit registration, but the new
behavior was additive: extension code and composition changed while stable
dispatch and checkout policy remained closed to modification.

### A10 Verification Snapshot

From each version directory, the following commands were run:

```powershell
python -m unittest discover -s tests -v
python -m store.main
```

At the A10/S10 experiment snapshot, the initial version passed 7 tests and the
applied version passed 14 tests. Both demos completed credit-card, bundle, and
cash checkout scenarios. S10 performed the final independent verification
after completing the OpenCode evaluation. Later post-experiment tests are
reported separately below and do not change this historical snapshot.

## Step 8: Evaluate OpenCode and Finalize the Experiment

This section records what OpenCode contributed, where its output had to be
corrected or rejected, the Skill's impact on the process, the prompts that
governed the work, possible process improvements, and the experiment's
conclusion. Everything below is supported by the repository history and the
recorded work in Steps 1-7.

### Correct OpenCode Contributions

- **Correctly detected all five SOLID violations with concrete file and symbol
  evidence.** The analysis in Step 2 identifies `order_service.py:OrderService`
  (SRP, DIP), `payment.py:PaymentProcessor.process` and
  `pricing.py:DiscountCalculator.calculate` (OCP), and
  `notification.py:SmsOnlyNotifier` / `NotificationService` (LSP, ISP), each
  with a stated maintenance or substitution risk.
- **Preserved the intentionally flawed initial version.**
  `01-Without-OOD-Principles` was treated as immutable, and every later change
  was directed at the applied version only.
- **Kept cash absent from the applied version until A9.** The refactoring
  phases and the S8 scope explicitly excluded cash, so the applied extension
  was measured separately from the refactoring itself.
- **Proposed payment handlers and registry dispatch.** Armin's A8 extracted
  credit-card, PayPal, and Bitcoin handlers behind a `PaymentHandler` contract
  and replaced the `if`/`elif` chain with registry dispatch.
- **Proposed constructor injection and composition-root wiring.** Soroush's S8
  moved concrete construction into `store/main.py`, so `OrderService` controls
  only injected collaborators.
- **Added characterization, unit, integration, and regression coverage.** The
  initial and applied versions each gained pre-cash characterization tests,
  cash unit tests, cash integration tests, and checkout regression tests.
- **Used Git ranges to make measurements reproducible.** The comparisons in
  Step 7 run `git diff --numstat` over explicit commit ranges rather than
  relying on recalled line counts.

### Corrected or Rejected Suggestions

- **Corrected the proposed applied baseline from the current cash-modified
  folder to commit `6908c62`.** The initial plan said "copy the pre-cash source
  state"; S7 redefined Phase 0 to copy the git tree at `6908c62`, where no
  `cash` branch and no cash order exist, instead of the already-modified
  `01-Without-OOD-Principles`.
- **Rejected an unnecessary receipt protocol.** Only one receipt printer exists
  and it has one public method, so a dedicated contract would have been an
  abstraction without a consumer.
- **Rejected an unused push notifier.** The checkout flow never sends push;
  implementing `PushNotifier` would have reproduced the unused operations that
  caused the original ISP violation.
- **Rejected separate directories for every handler and rule.** Handlers,
  notifiers, and discount rules stayed in the modules they belong to
  (`payment.py`, `notification.py`, `pricing.py`) instead of per-concept
  folders.
- **Corrected unclear A8/S8 file ownership.** The original plan did not state
  which files belong to which phase; S7 added a per-owner file table so the two
  contributors never edit the same files in the same phase window.
- **Resolved the A8 wiring conflict by temporarily allowing default payment
  handlers, leaving complete composition-root injection for S8.** A8 introduced
  the payment extension point while `OrderService` still constructed its
  collaborators and `main.py` still called `OrderService()` with no arguments.
  `PaymentProcessor` kept a default handler tuple so the existing workflow kept
  working; S8 then completed constructor injection and composition-root wiring.
  The post-experiment review later removed this fallback after finding that it
  omitted cash and diverged from the composition root.
- **Corrected the claim that SRP was completely solved.** `OrderService` still
  owns the use-case calculations, the paid-status transition, and message
  construction; Step 5 records SRP as "Improved", not fully resolved.
- **Clarified the initial test line count.** The 133 added test lines in
  `01-Without-OOD-Principles` were not all cash-specific: 70 characterize the
  pre-existing payment methods and 63 directly test cash.
- **Clarified interpreter wording.** Final verification in the target Windows
  environment uses `python`; the verification commands in this report retain
  `python` consistently.

### Skill Impact

The Skill at `.opencode/skills/solid-refactoring/SKILL.md` shaped the workflow
in measurable ways:

- **Required evidence before recommendations.** No finding was reported
  without a concrete file, symbol, confidence level, and realistic change that
  exposes the design cost.
- **Prevented edits before explicit approval.** Analysis and refactoring were
  separate phases, and the documented workflow requires user approval before
  editing.
- **Encouraged incremental, behavior-preserving changes.** Refactoring ran in
  small steps with tests after each group, preserving observable checkout
  behavior.
- **Prevented unrelated refactoring.** The Skill explicitly prohibits
  combining unrelated refactorings into the same change set.
- **Required tests after each implementation phase.** Every phase of the plan
  ran the applied test suite before the next phase began.
- **Made rejected suggestions and plan corrections visible.** Accepted,
  corrected, and rejected suggestions are recorded in Steps 1, 4, and 8 rather
  than being silently dropped.

**Human review was still necessary.** The corrections above (baseline commit,
A8/S8 ownership, SRP overstatement, test-line breakdown, interpreter wording)
were caught by manual review of the plan and the report, not by the Skill
itself. The Skill improves discipline but does not replace a factual review.

### Important Prompts

The prompts below were actually issued during the project. The constraints they
carried are what made each step reproducible:

- **"Do not refactor `01-Without-OOD-Principles`."** Kept the intentionally
  flawed design intact as the experiment's baseline.
- **"Add cash to the initial conditional design."** Directed the cash branch
  into the existing `if`/`elif` chain of the initial version, without
  refactoring it.
- **"Review all five SOLID principles with evidence."** Required every finding
  to cite a file, a symbol, and a concrete risk.
- **"Do not edit until the reviewed plan is approved."** Defined the intended
  separation between analysis, planning, and implementation.
- **"Keep cash absent from the applied version until A9."** Kept the
  refactoring and the extension as separate, measurable changes.
- **"Modify only the two A9 production files."** Scoped the applied cash
  extension to `store/payment.py` and `store/main.py`.

### Possible Process Improvements

- **Record important prompts immediately** rather than reconstructing them
  later; prompt intent is lost as sessions age.
- **Add an automated check for allowed files in each phase** so scope
  violations are caught by the toolchain instead of manual review.
- **Validate plan ownership against actual dependency requirements before
  implementation;** the A8/S8 ownership split needed a correction after review.
- **Use the documented `python` launcher consistently** for verification.
- **Automate Git range measurements** so change-effort numbers are regenerated
  by script rather than recomputed by hand.
- **Run a final factual review** to catch overclaimed SOLID corrections such
  as the SRP wording corrected above.

### Post-Experiment OpenCode Mode Compliance Review

This post-experiment review explicitly selected the real Plan agent, which used
the project Skill, remained read-only, compared the plan with the implementation,
and produced accepted, corrected, and rejected findings. Human review refined
the SRP wording and approved only verified corrections. The real Build agent
then applied each approved scope separately.

- Documentation corrections removed unsupported historical mode claims, fixed
  the plan status, test provenance, interpreter wording, and baseline hash, and
  recorded the review without changing the experiment measurements.
- The Plan agent identified inconsistent payment configuration: the implicit
  `PaymentProcessor()` defaults omitted cash while `build_payment_processor()`
  registered it. Build removed the implicit defaults, made handler registration
  mandatory, and routed built-in processor tests through the composition root.
- Build added the recommended regression coverage for discount precedence and
  rounding, validation boundaries, notification suppression, and the demo's
  bundle checkout path.

Current post-experiment verification passes 7 tests in the initial version and
25 tests in the applied version, and both demos complete successfully. The
historical A10/S10 snapshot remains 7 and 14 tests. These follow-up changes are
excluded from the original experiment metrics and do not alter their ranges or
values.

### Conclusion

SOLID did not necessarily reduce raw production line count: the applied cash
extension added a complete handler class (more lines than the initial
conditional branch), and the refactoring added contracts, rules, and wiring.
Its value was a reduction in modification risk. When cash was added to the
applied version, payment dispatch, all three existing handlers, and
`OrderService` remained unchanged; only a new handler and its composition-root
registration were added. The initial design, by contrast, required editing the
stable payment-dispatch conditional for every new method. The experiment
therefore shows that SOLID improved extensibility and regression safety rather
than raw size.
