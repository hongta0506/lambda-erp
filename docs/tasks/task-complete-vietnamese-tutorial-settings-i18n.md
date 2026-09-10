# Task: Complete Vietnamese Translation for Tutorial and Settings

**Status:** Completed  
**Date:** 2026-09-10  
**Target:** `frontend/src/i18n/locales/vi.json`

## 1. Problem Statement
Auditing `vi.json` against `en.json` revealed:
- 0 missing keys.
- But **134 keys still contained original English strings**.
- Major untranslated blocks:
  - `tutorial`: All 15 tutorial steps (titles, descriptions, tips), chips, links, custom analytics guide, setup guide, lifecycle notes.
  - `settings`: Chat API token management, personal bearer keys, revoke/delete confirmation dialogs, Public Access / Demo mode controls.

## 2. Requirements & Scope
- Translate all 134 remaining English strings in `frontend/src/i18n/locales/vi.json` to natural Vietnamese business and ERP terminology.
- Preserve placeholders like `{{version}}`, `{{key}}`, `{{name}}`.
- Keep standard technical terms (PDF, Email, API) clean and natural in Vietnamese.
- Validate JSON structure and verify 0 remaining untranslated English sentences.

## 3. Verification Plan
- Run Python audit script to confirm 0 missing keys and 0 untranslated text strings.
- Validate JSON syntax.
