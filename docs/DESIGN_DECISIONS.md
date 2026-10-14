# Design decisions

The choices that shaped Nova AI, and why.

## 1. Numbers come from code, words can come from a model

Every figure a user sees (revenue, margins, quality scores, forecasts) is computed
deterministically from the database. A language model may *narrate* those figures, but its
output passes through a mechanical sanitizer: generated SQL, URLs and secret-looking strings are
removed, and any number that does not appear in the computed context is replaced with
`[unverified figure removed]`.

**Why:** an analytics product loses all value the first time it shows a confident, wrong number.

## 2. Ask "can this be answered?" before asking a model anything

A deterministic answerability check classifies each question first: answerable from data,
partially answerable, needs a column mapping, needs more history, or not answerable safely
(for example requests for raw rows or credentials). The answer mode follows from that decision.

**Why:** honest "I can't answer that yet, here is what's missing" beats a fluent guess.

## 3. Forecasts are statistics, not generations

Two named methods only: seasonal-naive when at least two full seasons exist, otherwise a
least-squares trend. Each horizon has a minimum history (8 weeks for 90 days, 24 months for a
year). Confidence bands come from historical residuals. No model produces forecast values.

## 4. A multi-agent workflow with a quality gate

Pipeline requests run through a LangGraph graph: Discovery → Implementation → Quality →
Deployment → Monitoring. When the quality gate fails, a Reasoning agent proposes a repair and
implementation retries, up to a limit, before stopping with a recorded error. Every stage is
persisted and streamed to the UI.

## 5. Ingestion built for volume and reruns

Connectors implement one small protocol (`test_connection`, `extract_batches`). Large CSV loads
use PostgreSQL `COPY` into a staging table, a quality gate, then promotion to canonical records.
Runs are idempotent, so a retried job never double-counts revenue.

## 6. Tenant isolation everywhere

Every data query is scoped to the caller's workspace and checked for ownership. Authentication
is handled by Clerk with JWT verification on the backend.

## 7. Honest status, in writing

Each development phase ended with a written audit stating what was proven, what was only
tested locally, and what still needed a live environment. No feature is labelled
production-proven without evidence.

## 8. Ship through a gated pipeline on managed services

The API runs as a Docker container on Render, the dashboard on Vercel and the database on
Supabase (managed PostgreSQL). GitHub Actions gates every release: pull requests are linted,
type-checked and built, and get a Vercel preview; a merge to `main` builds the image, runs
Alembic migrations and the tests, then deploys. Configuration lives in environment variables,
and Sentry and UptimeRobot watch production. Managed services kept a small team focused on the
product instead of servers.
