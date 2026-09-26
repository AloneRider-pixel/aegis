# Verification & Evidence

| Area | Evidence | Reproduction |
|---|---|---|
| Policy authorization | tests/test_portfolio_execution_policy.py | pytest tests/test_portfolio_execution_policy.py -v |
| Failure simulation | backend/app/simulator/ | Run the documented simulator scenarios |
| Agent evaluation | docs/evaluation.md | Freeze scenario set, model/config, and expected labels before measurement |
| CI/CD | .github/workflows/ci.yml | GitHub Actions |
| Static security analysis | .github/workflows/codeql.yml | CodeQL |
| Workflow supply-chain posture | .github/workflows/scorecard.yml | OpenSSF Scorecard |

## Evidence policy

The current evaluation API uses synthetic demo metrics for workflow/UI validation. Those values are not treated as benchmark results.

Publishable model or reliability measurements must record dataset/scenario version, denominator, environment, application commit, model/configuration, timestamp, and exact command.