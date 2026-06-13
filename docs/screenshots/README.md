# Wave × BranchlessPay — M2 E2E Screenshots

Captured during M2 verification (2026-06-13). Live Wave invoice anchor + collector pipeline for all four event types.

| # | Wave event | BP `event_type` | Verify URL |
|---|------------|-----------------|------------|
| 1 | `invoice.created` | `wave_invoice_created` | https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4 |
| 2 | `invoice.updated` | `wave_invoice_updated` | https://branchlesspay.com/verify/555be781-8795-4549-b865-04d589f45577 |
| 3 | `payment.created` | `wave_payment_received` | https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1 |
| 4 | `transaction.created` | `wave_transaction_recorded` | https://branchlesspay.com/verify/80691be3-7f41-4345-8b7e-b466780aaa02 |

## Files

| File | Event |
|------|-------|
| [01_invoice_created.png](01_invoice_created.png) | Invoice created |
| [02_invoice_updated.png](02_invoice_updated.png) | Invoice updated |
| [03_payment_created.png](03_payment_created.png) | Payment received |
| [04_transaction_created.png](04_transaction_created.png) | Transaction recorded |

Events 1–2 used live Wave invoice #1 ($1,500). Events 3–4 validated via collector E2E (`scripts/e2e_collector_all_events.py`) with sample Wave documents and real BP anchor API.
