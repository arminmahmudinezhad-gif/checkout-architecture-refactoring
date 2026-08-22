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

### Verification

Run the initial version and its tests from the repository root:

```powershell
cd 01-Without-OOD-Principles
python -m unittest discover -s tests -v
python -m store.main
```

All seven tests pass, and the demo completes the credit-card, bundle, and cash
checkout scenarios.
