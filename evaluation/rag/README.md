# Synthetic RAG regression scaffold

This is an offline contract harness, not an LLM quality score or a production benchmark.
All questions, documents and candidate answers are synthetic. No model/API calls, secrets,
paid services or real incident data are used.

Run from the repository root:

```sh
python3 evaluation/rag/rag_eval.py --output rag-report.json
python3 -m unittest discover -s evaluation/rag -p 'test_*.py' -v
```

## What the numbers mean

- Retrieval hit-rate: fraction of answerable golden questions for which at least one
  expected document is in top-k. It tests an in-memory substring baseline modeled on
  the current HTTP endpoint, not the actual database endpoint or pgvector.
- Support proxy: every newline-separated answer claim must be an exact excerpt of a
  cited retrieved document. Negative fixtures cover fabricated remediation, incorrect
  and missing citations, unrelated answers, and safe abstention.
- Regression gate: compares per-case retrieval/support-check pass status against the
  committed baseline, rejects removed cases, and emits a JSON report and hit-rate delta.
  Baseline changes must be reviewed, not generated automatically in CI.

## Important limits and next work

Current `backend/app/main.py` knowledge search uses ILIKE plus an uncalibrated constant
score. `backend/app/ai/tools/runbooks.py` imports a knowledge_service module that does
not exist on the audited main commit. This harness does not repair either path and does
not imply the agent retrieval integration works.

The golden answers here are fixtures, not generated responses. Exact-quote support is a
conservative faithfulness proxy: it rejects legitimate paraphrases, does not understand
negation or contradictory context, and can accept irrelevant copied text. A perfect
synthetic result is expected and says nothing about production accuracy.

Next steps need a separate implementation review: wire an injectable live retriever,
run against seeded pgvector with service/environment filters, capture generated answers,
and add human-reviewed claim entailment and answer relevance labels. Keep all offline
results separate from live model evaluation, including model/version/cost metadata.
