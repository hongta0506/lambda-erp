# Task: Support OpenAI-Compatible Chat Completions in Report Specialist

**Status:** Completed  
**Date:** 2026-09-10  
**Target:** `api/chat.py`

## 1. Problem Statement
When running with custom LLM endpoints (`OPENAI_BASE_URL` set, `ERP_CHAT_API=chat`), `_generate_report_spec_via_openai` fails:
`Report specialist returned an invalid spec after 2 attempts: TypeError: 'NoneType' object is not iterable`

Root cause:
- `_generate_report_spec_via_openai` hardcoded `client.responses.create(...)`.
- Non-OpenAI / proxy endpoints (LiteLLM, vLLM, Gemini proxy) do not implement `/v1/responses`.
- Returned object lacks `output` structure, causing `NoneType` iteration failure in `content` parser.

## 2. Requirements & Scope
- Check `_use_responses_api()` inside `_generate_report_spec_via_openai`.
- If `False`, call `client.chat.completions.create(model=model, messages=[...], max_completion_tokens=4096)`.
- Extract response text directly via `response.choices[0].message.content`.
- Retain cost/usage logging and reservation settling for rate limiter.

## 3. Verification Plan
- Unit test / standalone call invoking `_generate_report_spec_via_openai` or simulating `_use_responses_api() == False`.
- Verify report spec JSON extracts cleanly without `TypeError`.
