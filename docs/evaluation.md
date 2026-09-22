# Evaluation Protocol

Aegis separates workflow validation from claims about model quality.

## Current state

The `/api/evaluations/run` path produces synthetic demo metrics so the evaluation UI and persistence flow can be exercised deterministically. These values are not presented as a benchmark of model accuracy.

## Benchmark requirements

A publishable agent benchmark should freeze:

- the incident scenario set
- telemetry and operational evidence available to the agent
- runbook/postmortem corpus version
- model/provider configuration
- tool permissions
- expected root-cause labels
- exact evaluation criteria

Each run should record the dataset version, application commit, model identifier, prompt/configuration revision, timestamp, and per-case result.

## Recommended measures

For root-cause analysis:

- exact-match or rubric-based correctness
- evidence citation/grounding rate
- false-positive and false-negative rates
- investigation latency
- tool-call count

For remediation:

- unsafe-action rejection rate
- approval-gate compliance
- rollback-path availability
- audit-trail completeness

## Reproducibility

Do not compare runs unless the scenario set and evaluation configuration are held constant. When reporting a result, include the denominator and the exact commit/configuration used.

See [Reviewer Guide](reviewer-guide.md) for the fastest technical review path.
