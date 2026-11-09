# Privacy Notice

_Last updated: 2026-11-09_

## What this service does

The Mood Librarian recommends a literary work based on a short description of
your mood that you submit to the `/recommend` endpoint.

## What data we process

- **Your mood text.** It is sent to a third-party LLM provider (Groq) and to
  search services (OpenLibrary, DuckDuckGo) to generate a recommendation.
- Mood descriptions can reveal information about your emotional or mental-health
  state, which may constitute **sensitive / special-category data** under the
  EU GDPR (Art. 9). We treat it accordingly.

## What we store

- **We do not persist your mood text.** It is held in memory only for the
  duration of the request and is not written to any database or log file.
- Server logs record **non-identifying operational metrics only** (latency,
  token counts, quality score) — never the content of your request.

## Third parties

Your mood text is transmitted to:

- **Groq** — LLM inference (see Groq's privacy policy).
- **OpenLibrary** and **DuckDuckGo** — search queries derived from the request.

We do not control how these providers process data; review their policies.

## Your rights (GDPR)

Because we do not store personal data, there is normally nothing to access,
rectify, or erase. For any question, contact the service operator.

## Children

This service is not directed at children.

## Changes

This notice may be updated; the date above reflects the latest version.
