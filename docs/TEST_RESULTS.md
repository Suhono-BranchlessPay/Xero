# Test Results — Xero BP Collector

Branch: `dev`

---

## Automated tests

| Suite | Result |
|-------|--------|
| `tests/test_signature.py` | PASS |
| `tests/test_normalizer.py` | PASS |
| `tests/test_webhook_handler.py` | PASS |
| `display/tests/xeroVerifyMapping.test.mjs` | PASS |

Run: `powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1`

---

## Production E2E

Pending Xero developer app + OAuth + ngrok webhook + BP test token.

Contact: suhono@branchlesspay.com
