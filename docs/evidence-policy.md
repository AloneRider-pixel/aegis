# Evidence and reproducibility policy

Aegis separates product capability, synthetic demo behavior, and measured model performance.

## Evaluation evidence

Any published root-cause, investigation, remediation, latency, reliability, or cost result should identify the scenario or dataset version, environment, configuration, sample count, scoring method, timestamp, and commit. Preserve the generated output when practical.

## Synthetic scenarios

The failure simulator is intentionally reproducible and safe for demos. Simulator results demonstrate workflow behavior; they are not evidence that an AI system will diagnose arbitrary real production incidents at the same rate.

## Model metrics

Model-quality claims should be based on a fixed evaluation set and a documented protocol. UI-generated demo metrics must stay labeled as synthetic.

## CI boundary

CI proves the configured code, tests, build, and static-analysis checks passed. It does not establish production incident-response effectiveness.
