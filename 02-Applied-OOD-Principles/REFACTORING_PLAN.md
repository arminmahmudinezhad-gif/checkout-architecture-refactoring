# SOLID Refactoring Plan

Status: Proposed by Armin; awaiting Soroush's S7 review and user approval.

## Goal

Create a behavior-preserving copy of the original checkout system, refactor it
to address the documented SOLID violations, and then add cash payment again.
The applied version must remain independently runnable under
`02-Applied-OOD-Principles` and must not import code from
`01-Without-OOD-Principles`.

## Constraints

- Treat commit `6908c62` as the pre-cash behavioral baseline.
- Do not modify `01-Without-OOD-Principles` during the refactoring.
- Preserve credit-card, PayPal, Bitcoin, unknown-method, pricing, persistence,
  notification, and receipt behavior unless the reviewed plan explicitly says
  otherwise.
- Keep the refactoring separate from the later cash extension so the cost of
  adding cash can be measured accurately.
- Run the applied-version tests after every implementation phase.
- Apply only the steps approved after S7 review.

## Target Design

### Payment Extension Point

Introduce a small payment-handler contract with a method identifier and a
`process(order, amount)` operation. Implement credit-card, PayPal, and Bitcoin
as separate handlers. A payment processor will dispatch through injected
handlers instead of an `if`/`elif` chain.

Adding cash later should require a new cash handler and composition-root
registration, without editing the existing handlers, payment processor, or
order workflow.

### Discount Extension Point

Represent VIP, bulk-order, and welcome-coupon discounts as separate rules.
`DiscountCalculator` will evaluate injected rules in the existing priority
order and return the first applicable discount, preserving current behavior.

### Focused Notification Contracts

Replace the broad multi-channel notification inheritance hierarchy with one
small notifier contract exposing `send(customer, message)`. Implement email,
SMS, and push as independent notifiers. The checkout workflow will receive the
enabled notifier collection rather than selecting channel-specific methods.

### Inverted Checkout Dependencies

Define structural contracts for the high-level dependencies used by
`OrderService`: pricing, payment, order persistence, notification, and receipt
output. Inject those collaborators through the constructor. Build concrete
objects in `store/main.py`, which acts as the composition root.

### Focused Responsibilities

Keep `OrderService` as the checkout use-case orchestrator. Move receipt
formatting to a receipt printer and move order validation to a validator. The
service may sequence validation, pricing, payment, persistence, notification,
and receipt output, but it should not implement those details.

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
    `-- test_payment.py
```

The reviewed plan may adjust filenames when that reduces unnecessary
abstractions, but the initial and applied versions must remain isolated.

## Implementation Phases

### Phase 0: Establish The Applied Baseline

1. Copy the pre-cash source behavior into `02-Applied-OOD-Principles/store`.
2. Add characterization tests for the existing payment methods and checkout
   behavior.
3. Run the tests and demo before refactoring.

Expected result: the applied folder reproduces the original behavior and does
not yet support cash.

### Phase 1: Introduce Payment Abstractions

Owner: Armin A8.

1. Define the payment-handler contract.
2. Extract credit-card, PayPal, and Bitcoin handlers from the conditional
   branches.
3. Make the payment processor dispatch through injected handlers.
4. Preserve receipt tokens, formatted amounts, messages, and unknown-method
   errors.
5. Add or adapt focused payment tests.

Expected result: existing payment methods pass without a central payment
conditional, and cash is still absent.

### Phase 2: Decouple The Checkout Workflow

Owner: Soroush S8.

1. Extract channel-specific notifiers behind the focused notifier contract.
2. Introduce discount-rule implementations while preserving rule priority.
3. Add persistence, pricing, validation, and receipt-output contracts where
   required by `OrderService`.
4. Inject collaborators into `OrderService` rather than constructing them
   internally.
5. Move concrete construction to `store/main.py`.
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
payment dispatch, or `OrderService`.

### Phase 4: Verify The Applied Version

Owner: Soroush S9.

1. Add focused tests for the cash handler.
2. Add an integration test for cash through the refactored `OrderService`.
3. Run regression tests for existing payment methods and checkout behavior.
4. Run the complete demo and record the results.

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

## Acceptance Criteria

- Both version folders run independently.
- The initial version remains unchanged after its Step 1 implementation.
- Existing checkout behavior is covered by regression tests.
- `PaymentProcessor` contains no payment-method conditional chain.
- Adding cash does not modify existing payment handlers or `OrderService`.
- Notification implementations expose no unsupported inherited operations.
- `OrderService` receives its external collaborators through injection.
- Discount-rule priority and all receipt tokens remain unchanged.
- The final README explains S7 plan corrections and compares measured changes
  required to add cash in both versions.

## Review Questions For S7

1. Does the design preserve every behavior demonstrated by the initial tests?
2. Are any proposed contracts unnecessary for this project's size?
3. Are phase ownership and file boundaries clear enough to avoid overlapping
   commits?
4. Can cash be added in Phase 3 without modifying stable checkout classes?
5. Are the verification commands and acceptance criteria sufficient?
