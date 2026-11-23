# Security Policy

## Reporting a vulnerability

If you find a security issue, please **do not open a public issue**. Instead,
email the maintainer (see the GitHub profile) with:

- a description of the issue and its impact,
- steps to reproduce,
- any suggested fix.

You can expect an acknowledgement within a few days.

## Scope & posture

This is a public demo service. Security measures in place:

- **No persistence** of user input — mood text is never stored (see `PRIVACY.md`).
- **Secrets** live only in environment variables (`GROQ_API_KEY` in the host),
  never in the repository. `.env` is git-ignored.
- **Per-IP rate limiting** (per-minute and per-day) to limit abuse and cost.
- **Input validation** (length-capped, non-empty) on every request.
- **Request timeouts** and safe error responses (no internal details leaked).
- **Baseline security headers** (CSP, `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`).
- **Branch protection**: changes reach production only via a reviewed PR with
  passing CI.
- **Dependabot** keeps dependencies and GitHub Actions up to date.

## Out of scope

The LLM responses themselves are AI-generated and may be inaccurate; see
`DISCLAIMER.md`.
