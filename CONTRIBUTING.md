# Contributing to Aegis

Aegis is maintained as an engineering portfolio project focused on reliable AI-assisted incident response.

## Development workflow

1. Create a focused branch from `main`.
2. Keep changes small and explain the engineering trade-offs in the commit or pull request.
3. Add or update tests for behavioral changes.
4. Run the same lint and test commands used by CI before opening a pull request.
5. Do not commit secrets, API keys, production data, or generated credentials.

## Quality expectations

- Prefer typed, modular code with clear boundaries between API, domain, infrastructure, and AI orchestration layers.
- Preserve authentication and authorization requirements on protected routes.
- Keep AI behavior observable and evaluable; avoid claims that cannot be reproduced from the repository.
- Update documentation when architecture, configuration, or public behavior changes.

## Pull requests

PRs should include a concise summary, testing performed, and any operational or security considerations introduced by the change.
