# Submission to BranchlessPay — Xero M1–M4

**To:** suhono@branchlesspay.com  
**Subject:** Xero integration scaffold ready — dev branch

---

## GitHub

https://github.com/Suhono-BranchlessPay/Xero/tree/dev

---

## Summary

- **M1:** Flask webhook `POST /webhook/xero` with `x-xero-signature` + intent-to-receive
- **M2:** Xero REST fetch + normalize + BP anchor POST with retry queue
- **M3+M4:** `display/src/xeroVerifyMapping.ts` + integration example for verify page

---

## Blockers / next steps

1. BP test token (`BP_LICENSE_KEY`) for live anchor test
2. Xero developer app + OAuth token + tenant ID
3. ngrok tunnel for webhook registration
4. BP production `VerifyPage.tsx` — add Xero branch (same pattern as Wave 770f391)

Contact: suhono@branchlesspay.com
