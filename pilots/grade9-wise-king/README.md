# Grade 9 — Wise King listening pilot

Status: teacher-facing static preview only. Not an operational or secured assessment.
Source supplied by teacher: https://www.youtube.com/watch?v=UjMiETlCwo0
Video audio and transcript have not been retrieved or verified.
All six questions are preserved from the teacher. No answer key or transcript is included.

## Pending inputs and services
- Exact student email domain and identity provider (Google Workspace or Microsoft).
- Authorized backend project and provider OAuth configuration.
- Private audio asset verified against the linked recording.
- Teacher-approved marking key and scoring scheme.

## Required server behavior before release
- Deny access by default while school identity configuration is missing.
- Verify provider tokens server-side (signature, issuer, audience, expiry and organization membership); do not trust a typed email, UI domain hint or editable profile metadata.
- Authorize enrolled students for this assessment.
- Keep student records, answer keys and media out of the public repository.
- Use persistent per-student/per-assessment counters. Reserve a play atomically, with idempotency for network retries; deny simultaneous active sessions and starts after three authorized plays.
- Authorize media requests, use short-lived playback access and private storage.
- Do not treat signed media URLs or hidden controls as protection against recording or copying.
- Save submissions server-side, validate question IDs and values, and make final submission idempotent.
- Provide teacher-only audited exception handling for interrupted playback.

## Release checks
Outside-domain account denied; unauthenticated media denied; changing browser does not reset plays; concurrent requests cannot exceed three; expired playback access denied; transcript/answer key absent from client; duplicate submission safe.

The static preview intentionally has no active sign-in, audio or submission. It is not linked from the Grade 8 site and this branch has not been merged or deployed.
