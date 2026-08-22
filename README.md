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

- The prompted `python -m unittest ...` command was corrected to `python3 -m
  unittest ...` because `python` is not resolvable on PATH in this environment.
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

## Step 3: Refactoring Plan Review (S7)

Armin's A7 proposed `02-Applied-OOD-Principles/REFACTORING_PLAN.md`. Soroush
reviewed it against the five SOLID violations from Step 2 and refined it in
the same file. The plan remains a proposal until the user approves it.

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
- The verification commands were noted to use `python3` in this environment
  while the original plan wrote `python`.

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

Additionally, the plan status was changed from *proposed* to *reviewed and
awaiting user approval*, a violation-to-correction mapping table was added,
an abstraction-simplification section was added, a file-ownership table was
added, and the acceptance criteria now include the requirement that no cash
logic exists in the applied folder before Phase 3.
