# ADRs / Decisions

This directory contains Architecture Decision Records (ADRs) for significant technical choices.

Conventions

- File names: Use the prefix ADR-<NNN>-short-description.md where <NNN> is a sequential integer. Use zero padding for easier sorting (e.g., ADR-001, ADR-002).
- Status: Each ADR should include a Status field (Proposed, Accepted, Superseded, Deprecated).
- Content: Include Date, Context, Decision, Alternatives, Consequences, and any follow-up actions.
- Location: Add new ADRs to this directory. Do not delete old ADRs — if a decision changes, create a new ADR that supersedes the previous one and reference it.

Quick Example

ADR-002-cohere-reranker.md — decision to add a Cohere-based reranking stage for child/parent candidate reordering.

Purpose

ADRs capture the reasoning behind decisions so future contributors and automated agents can understand why a particular approach was chosen.

Questions

If you're unsure whether a change warrants an ADR, prefer writing a short ADR. It's easier to consolidate later than to recreate historical context.
