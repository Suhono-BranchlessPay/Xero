# Milestone — Xero × BranchlessPay (M1 + M2)

Repo: https://github.com/Suhono-BranchlessPay/Xero  
Branch: **`dev` only**  
Status: **Production complete** — BP merged (`db11427` mapping, `7f3f7e6` enrichment)

---

## M1 — Webhook receiver

| Deliverable | Status |
|-------------|--------|
| `POST /webhook/xero` | ✅ |
| `x-xero-signature` HMAC-SHA256 (Base64) | ✅ |
| Intent-to-receive validation | ✅ LIVE on BP |
| Parse Xero batched webhook JSON | ✅ |
| Dev simulate script | ✅ |
| Docs | ✅ |

Production webhook: `https://branchlesspay.com/api/v1/webhook/xero`

---

## M2 — Normalize + BP anchor

| Deliverable | Status |
|-------------|--------|
| Xero REST client (`xero_client.py`) | ✅ |
| Normalizer + BP poster | ✅ |
| Idempotency + failed queue | ✅ |
| OAuth auto-refresh | ✅ (`7f3f7e6`) |
| Unit tests | ✅ |
| Live E2E (5 events, 3 invoices) | ✅ |

**Live verify URLs (anchored on Monad):**

| Event | Verify URL |
|-------|------------|
| INV-0001 Create | https://branchlesspay.com/verify/85c80ab2-5014-4d87-a5ed-62eb4851e244 |
| INV-0002 Create | https://branchlesspay.com/verify/21309f86-e1c1-4010-91f7-61ff853bab38 |
| INV-0002 Update | https://branchlesspay.com/verify/6c005b64-9c0f-49cf-9cf6-804db5630801 |
| INV-0003 Create | https://branchlesspay.com/verify/f90bae2f-7e1a-47cb-bb0f-515cee0edf12 |
| INV-0003 Update | https://branchlesspay.com/verify/eece8209-9264-4e87-aaa6-397f808d8651 |

---

## M3 + M4 — See [MILESTONE_M3_M4.md](MILESTONE_M3_M4.md)

Contact: suhono@branchlesspay.com
