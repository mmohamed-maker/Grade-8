# Security implementation — deployment pending

Confirmed: Google Workspace; hosted domain ikns.edu.bh; exact student-email allowlist; three plays; a teacher-defined assessment window in Asia/Bahrain.

## Files
- schema.sql: private roster and assessment records; server-only atomic reservation RPC.
- supabase/functions/listening-gate/index.ts: verifies Google ID tokens cryptographically, then checks exact email membership and server time via RPC.
- policy.mjs and policy.test.mjs: additional identity/request validation and 13 passing unit tests.
- client.js: Google sign-in and playback integration, inactive until public configuration is supplied.
- supabase/config.toml: disables Supabase-JWT gateway validation because this endpoint verifies Google ID tokens itself.

## Deployment checklist
1. Create/authorize a Supabase project; apply schema.sql. The assessment is disabled and roster empty by default.
2. Create a PRIVATE storage bucket named listening-private; grant no anon/authenticated read or write policies. Upload verified audio privately.
3. Configure a Google OAuth web client with the exact frontend origin. The frontend uses Google Identity Services; server verifies audience, issuer, expiry, signature, email_verified, hd and Google sub. hd on the client is only a hint.
4. Set GOOGLE_CLIENT_ID and ALLOWED_ORIGIN as function secrets. SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are runtime secrets, never public files.
5. Copy the handler and policy into the indicated Supabase function layout and deploy listening-gate. Pin dependency patch versions/lockfile during deployment.
6. Import real roster through the private administrator database only. Do NOT commit student emails to this public repository.
7. Set opens_at and closes_at with the ACTUAL date and explicit +03:00 offset, audio_path and measured audio_seconds, then enable assessment after integration tests pass. No date/time is preselected; 08:00–09:00 was an example.
8. Set only public OAuth client ID and HTTPS function endpoint in client.js.
9. Run real Google sign-in, database concurrency, time boundary, storage access and browser audio tests before merging/publishing.

## Behavior and limitations
A roster entry binds to the first verified Google subject. Counters persist across devices. Row locking serializes concurrent starts. A UUID retry key avoids duplicate charges and does not extend a 60-second media URL. New starts are blocked while the previous audio-duration lease remains active. A play is refused if the whole audio no longer fits before closing time.

The assessment window gates server access and new media URLs. Media already delivered cannot be revoked; short-lived signed URLs can be reused within their lifetime. Downloading, recording, sharing credentials or transcription by outside tools cannot be prevented absolutely. This is a three-session authorization limit, not DRM.

There is no active submission/grading or teacher exception UI yet. There is no automatic refund after media errors, because that could enable unlimited replay; teacher audit tooling remains pending. Existing preview questions are public repository content; do not treat their text as confidential. Transcript and answer key are absent.

## Verification performed
13 local Node unit tests pass for identity/request policy. PostgreSQL, Supabase deployment, Google OAuth and browser integration have NOT been executed in this environment. This is implementation awaiting integration, not a live secured assessment.
