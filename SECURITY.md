# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues.

Report suspected vulnerabilities privately through the repository's GitHub security reporting mechanism when available, including:

- affected component or endpoint
- reproducible steps
- expected vs. observed behavior
- relevant logs or sanitized evidence

Do not include API keys, passwords, tokens, personal data, or other secrets.

## Security practices

- Secrets are supplied through environment variables or the deployment secret store.
- Production CORS origins should be explicitly configured.
- Authentication and authorization are required for protected API operations.
- Dependency and CodeQL checks run through GitHub Actions.
