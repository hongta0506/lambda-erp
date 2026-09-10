# Task: Complete Vietnamese Localization (i18n)

**Status:** Completed  
**Date:** 2026-09-10  
**Target:** `frontend/src/i18n/locales/vi.json`

## 1. Problem Statement
The initial Vietnamese translation added to `frontend/src/i18n/locales/vi.json` was incomplete:
- **58 keys missing** entirely compared to `en.json` (including `bankReconciliation`, `chat`, `status`, `titles`).
- **~190 keys untranslated**, retaining original English values (notably in `settings`, `security`, `userManagement`, `password`).

## 2. Requirements & Scope
- Translate all missing keys from `en.json` into natural Vietnamese business/ERP terminology.
- Translate untranslated keys in `vi.json` without breaking placeholder tokens (e.g., `{{count}}`, `{{name}}`).
- Maintain exact key hierarchy and parity with `en.json`.
- Ensure JSON validity and test formatting.

## 3. Key Sections Covered
1. **Chat & Assistant**: Prompts, input placeholders, clear history, model info, error messages.
2. **Bank Reconciliation**: Unreconciled transactions, matching, statement upload, clearance dates.
3. **Document Statuses & Titles**: Invoices, payments, purchase orders, delivery notes, journal entries.
4. **Settings & Security**: Password changes, 2FA/MFA, user roles, company info, preferences.

## 4. Verification Plan
- Python script to verify:
  1. `vi.json` parses as valid JSON.
  2. Missing keys count against `en.json` is `0`.
- Verify frontend bundle compilation (npm build or typecheck) if applicable.
