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

### Verification

Run the initial version and its tests from the repository root:

```powershell
cd 01-Without-OOD-Principles
python -m unittest discover -s tests -v
python -m store.main
```

All seven tests pass, and the demo completes the credit-card, bundle, and cash
checkout scenarios.
