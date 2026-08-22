# SOLID Refactoring Plan

Status: Phases 0-4 were implemented and verified.
The reviewed plan was completed; this document records the implemented
refactoring and verification scope.

## Goal

Create a behavior-preserving copy of the original checkout system, refactor it
to address the documented SOLID violations, and then add cash payment again.
The applied version must remain independently runnable under
`02-Applied-OOD-Principles` and must not import code from
`01-Without-OOD-Principles`.

## Constraints

- Treat commit `6908c62` as the pre-cash behavioral baseline. This was verified
  in S7 against the git history: at `6908c62` the working `store/` tree contains
  no `cash` branch in `payment.py` and no cash order in `main.py`, and the
  snapshot commit `bf7a03b` copied that exact tree into
  `01-Without-OOD-Principles`.
- Copy the applied baseline from the git tree at commit `6908c62`
  (`git archive 6908c62 store`), not from the current
  `01-Without-OOD-Principles`, which is already cash-modified.
- Do not modify `01-Without-OOD-Principles` during the refactoring.
- Preserve credit-card, PayPal, Bitcoin, unknown-method, pricing, persistence,
  notification, and receipt behavior unless the reviewed plan explicitly says
  otherwise.
- Keep the refactoring separate from the later cash extension so the cost of
  adding cash can be measured accurately.
- Do not introduce any `cash` branch or cash order in
  `02-Applied-OOD-Principles` before Phase 3 (Armin's A9).
- Run the applied-version tests after every implementation phase.
- The approved steps were implemented through Phases 0-4.

## S7 Review: Violation-to-Correction Mapping

Every documented SOLID violation maps to an explicit correction phase below.

| Principle and location | Current defect | Correction | Phase | Owner |
| --- | --- | --- | --- | --- |
| SRP — `order_service.py` `OrderService` | The initial service owns validation rules, shipping/total calculation, status transition, notification-message construction, and receipt output while constructing concrete collaborators | Extract validation and receipt output, inject collaborators, and retain use-case orchestration and calculations in `OrderService` | Phase 2 | Soroush S8 |
| OCP — `payment.py` `PaymentProcessor.process` | Adding a method adds another branch to a central `if`/`elif` chain | Define a payment-handler contract and registered handlers (credit card, PayPal, Bitcoin); later cash is a new handler plus registration | Phase 1, 3 | Armin A8, A9 |
| OCP — `pricing.py` `DiscountCalculator.calculate` | Adding a rule adds a branch to the discount chain | Evaluate an injected ordered list of discount rules, preserving priority | Phase 2 | Soroush S8 |
| LSP — `notification.py` `SmsOnlyNotifier` | Subtype raises `NotImplementedError` for inherited email and push, so it cannot substitute `NotificationService` | Remove the inheritance relationship and define a single-`send` notifier contract that every notifier fully implements | Phase 2 | Soroush S8 |
| ISP — `notification.py` `NotificationService` | Clients are forced to depend on email, SMS, and push operations even for a single channel | Split Email, SMS, and push into independent notifier implementations; the workflow receives only the notifiers it uses | Phase 2 | Soroush S8 |
| DIP — `order_service.py` `OrderService.__init__` | The checkout workflow constructs and depends on concrete classes | Inject collaborators through the constructor; concrete construction happens only in the composition root in `main.py` | Phase 2 | Soroush S8 |

## S7 Review: Abstraction Simplifications

The following proposed abstractions were removed or simplified:

- The dedicated receipt-formatting contract was dropped. The receipt printer is
  kept as a single concrete class with one public method, and `OrderService`
  depends on that method's behavior instead of a dedicated interface. It has no
  second implementation, so a protocol would be an abstraction without a use.
- The push notification channel is not implemented in the applied version
  because the checkout workflow never sends push. Only `EmailNotifier` and
  `SmsNotifier` are planned, which removes the unused operations that caused
  the ISP finding to begin with.
- Handlers, notifier implementations, and discount rules each live with the
  module concept they implement (`payment.py`, `notification.py`, `pricing.py`)
  rather than a separate rule/handler directory.
- All remaining structural contracts (payment, pricing, persistence, and
  notification) live in a single `contracts.py`, which avoids one-file-per-
  contract overhead at the project's size.

## Target Design

### Payment Extension Point

Introduce a small payment-handler contract with a `method` identifier and a
`process(order, amount)` operation. Implement credit-card, PayPal, and Bitcoin
as separate handlers. A payment processor will dispatch through injected
handlers instead of an `if`/`elif` chain.

Adding cash later requires a new cash handler and composition-root
registration, without editing the existing handlers, payment processor, or
order workflow.

### Discount Extension Point

Represent the VIP, bulk-order, and welcome-coupon discounts as separate rule
objects. `DiscountCalculator` evaluates the injected, priority-ordered rule
list and reduces to the first applicable discount, preserving current behavior.

### Focused Notification Contracts

Replace the broad multi-channel `NotificationService` and its
`SmsOnlyNotifier` inheritance with one small notifier contract exposing a
single `send(customer, message)` operation. Implement `EmailNotifier` and
`SmsNotifier` as independent classes. The checkout workflow receives the
enabled notifier collection rather than invoking channel-specific methods.

### Inverted Checkout Dependencies

Define contracts for pricing, payment, persistence, and notification.
Inject those collaborators into `OrderService` through the constructor. Build
the concrete objects in `store/main.py`, which acts as the composition root.

### Focused Responsibilities

Keep `OrderService` as the checkout use-case orchestrator. Move order
validation behind a validator, move receipt formatting into the printer, and
keep pricing, persistence, and notification behind their injected
collaborators. The service only sequences these steps.

## Planned File Structure

```text
02-Applied-OOD-Principles/
|-- REFACTORING_PLAN.md
|-- store/
|   |-- contracts.py
|   |-- main.py
|   |-- models.py
|   |-- notification.py
|   |-- order_service.py
|   |-- payment.py
|   |-- pricing.py
|   |-- receipt.py
|   |-- storage.py
|   `-- validation.py
`-- tests/
    |-- test_existing_payments.py
    |-- test_order_service.py
    |-- test_payment.py
    `-- test_cash_checkout.py
```

`contracts.py` and `main.py` are owned by different phases sequentially (see
the ownership table below), so their edits never overlap on a working branch.

## A8 / S8 File Ownership

| Phase | Owner (commit) | Files edited | Out of scope |
| --- | --- | --- | --- |
| Phase 0 — baseline | Armin A8 (preparatory commit) | `02-Applied-OOD-Principles/store` copied from the `6908c62` tree; tests separately created/adapted | No cash logic anywhere; no refactoring |
| Phase 1 — payment abstractions | Armin A8 | `store/contracts.py` (payment contract only), `store/payment.py`, `store/main.py` (wiring in composition root unchanged otherwise), `tests/test_payment.py` | `notification.py`, `pricing.py`, `order_service.py`, `storage.py`, `receipt.py`, `validation.py` |
| Phase 2 — decouple workflow | Soroush S8 | `store/contracts.py` (pricing, persistence, notification contracts), `store/notification.py`, `store/pricing.py`, `store/storage.py`, `store/receipt.py`, `store/validation.py`, `store/order_service.py`, `store/main.py`, `tests/test_order_service.py`, `tests/test_existing_payments.py` | `store/payment.py`, `tests/test_payment.py` |
| Phase 3 — cash extension | Armin A9 (new cash handler) | `store/payment.py` (add `CashHandler`), `store/main.py` (composition-root registration and demo cash order) | No edits to `order_service.py` or existing handlers |
| Phase 4 — verify applied version | Soroush S9 | `tests/test_cash_checkout.py`, regression test runs, demo runs | Production code |

`store/models.py` is copied in Phase 0 and is not modified afterward unless a
later phase explicitly requires it.

## Implementation Phases

### Phase 0: Establish The Applied Baseline

1. Copy the `store/` tree from commit `6908c62` into
   `02-Applied-OOD-Principles`.
2. Separately create or adapt characterization tests for the existing payment
   methods and checkout behavior; commit `6908c62` contains no tests.
3. Run the tests and demo before refactoring.

Expected result: the applied folder reproduces the original behavior and does
not yet support cash.

### Phase 1: Introduce Payment Abstractions

Owner: Armin A8.

1. Define the payment-handler contract in `contracts.py`.
2. Extract credit-card, PayPal, and Bitcoin handlers from the conditional
   branches.
3. Make the payment processor dispatch through injected handlers.
4. Preserve receipt tokens, formatted amounts, messages, and unknown-method
   errors.
5. Add or adapt focused payment tests.
6. Do not introduce any `cash` handler in this phase.

Expected result: existing payment methods pass without a central payment
conditional, and cash is still absent.

### Phase 2: Decouple The Checkout Workflow

Owner: Soroush S8.

1. Extract `EmailNotifier` and `SmsNotifier` behind the focused notifier
   contract; delete the `NotificationService`/`SmsOnlyNotifier` hierarchy.
2. Introduce discount rule implementations while preserving rule priority.
3. Move receipt printing and order validation behind the receipt printer and
   validator.
4. Inject collaborators into `OrderService` rather than constructing them
   internally.
5. Move concrete construction to the composition root in `store/main.py`.
6. Run regression tests and the demo.

Expected result: `OrderService` coordinates abstractions, notifier subtypes do
not expose unsupported methods, and current checkout behavior is preserved.

### Phase 3: Add Cash As An Extension

Owner: Armin A9.

1. Add a cash payment handler as a new implementation.
2. Register it in the composition root.
3. Add a realistic cash order to the applied demo.
4. Record every production file changed and the exact line counts.

Expected result: cash works without changing existing payment handlers,
payment dispatch, or `OrderService`. Compare with the change inventory of
Step 1.

### Phase 4: Verify The Applied Version

Owner: Soroush S9.

1. Add focused unit tests for the cash handler.
2. Add an integration test for cash through the refactored `OrderService`.
3. Run regression tests for existing payment methods and checkout behavior.
4. Run the complete CLI and record the results.

Expected result: all existing and cash scenarios pass in the applied version.

## Verification Commands

Run from `02-Applied-OOD-Principles`:

```powershell
python -m unittest discover -s tests -v
python -m store.main
```

After implementation, also confirm that the initial version still passes:

```powershell
cd ..\01-Without-OOD-Principles
python -m unittest discover -s tests -v
python -m store.main
```

The tested commands use `python`; retain those commands when running locally.

## Acceptance Criteria

- Both version folders run independently.
- The initial version remains unchanged after its Step 1 implementation.
- Existing checkout behavior is covered by regression tests.
- `PaymentProcessor` contains no payment-method conditional chain.
- Cash is not present in `02-Applied-OOD-Principles` before Phase 3 (A9).
- Adding cash does not modify existing payment handlers or `OrderService`.
- Notification implementations expose no unsupported inherited operations.
- `OrderService` receives its external collaborators through injection.
- Discount-rule priority and all receipt tokens remain unchanged.
- The final README explains S7 plan corrections and compares measured changes
  required to add cash in both versions.

## S7 Review Outcomes

The original A7 plan was reviewed against the five documented violations and
revised as follows.

- The five-phase structure was retained because the phases map one-to-one onto
  the violations mapped above (Phase 1 for payment-O part of OCP, Phase 2 for
  SRP, discount-OCP, LSP, ISP, and DIP, Phase 3 for the cash extension, Phase 4
  for verification).
- The baseline commit was verified from `git` history as `6908c62`, and the
  phase-0 copy instruction was made explicit, including the existing branch
  between `6908c62` and your current `01-Without-OOD-Principles` (the latter
  already contains cash).
- A8 and S8 file ownership is documented in the table above so the two
  contributors never edit the same files within the same phase window.
- The concrete dependency map at commit `6908c62` is unchanged by this review
  and remains the "before" state for the final A10 comparison.
