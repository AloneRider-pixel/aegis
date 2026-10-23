"""Synthetic RAG contract evaluation. No model calls or production benchmark claims."""
import argparse
import json
from pathlib import Path


def retrieve(query, documents, top_k=3):
    """Deterministic substring baseline, matching the current HTTP search design.

    Not pgvector, not an evaluation of the missing knowledge_service module.
    Input order is explicit because the current API has no relevance ordering.
    """
    return [d for d in documents if query.casefold() in d['content'].casefold()][:top_k]


def supported(answer, citations, retrieved):
    """Conservative exact-quote support proxy, NOT semantic faithfulness.

    Every nonempty claim must be an exact excerpt of a cited retrieved document.
    Empty answers fail: abstentions are handled separately by the runner.
    """
    by_id = {d['id']: d['content'] for d in retrieved}
    claims = [c.strip() for c in answer.split('\n') if c.strip()]
    return bool(claims) and bool(citations) and all(
        citation in by_id for citation in citations
    ) and all(any(claim in by_id[c] for c in citations) for claim in claims)


def evaluate(data):
    rows = []
    for case in data['cases']:
        docs = retrieve(case['query'], data['documents'], case.get('top_k', 3))
        ids = [d['id'] for d in docs]
        expected = set(case['relevant_ids'])
        hit = bool(expected.intersection(ids)) if expected else not ids
        answer = case['answer']
        if case.get('abstain', False):
            grounded = not expected and not ids and not answer and not case['citations']
        else:
            grounded = supported(answer, case['citations'], docs)
        rows.append({'id': case['id'], 'retrieved_ids': ids,
                     'retrieval_pass': hit, 'support_proxy': grounded,
                     'expected_support': case['expected_support'],
                     'support_check_pass': grounded == case['expected_support']})
    positives = [r for r, c in zip(rows, data['cases']) if c['relevant_ids']]
    return {'dataset': 'synthetic-golden-v1', 'mode': 'offline-substring-baseline',
            'limitations': ['No LLM generation', 'No semantic faithfulness judge',
                           'No live pgvector retrieval', 'Exact-quote support only'],
            'retrieval_hit_rate': sum(r['retrieval_pass'] for r in positives) / len(positives) if positives else 0,
            'contract_pass': all(r['retrieval_pass'] and r['support_check_pass'] for r in rows),
            'cases': rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default=str(Path(__file__).with_name('golden.json')))
    parser.add_argument('--output', default='rag-report.json')
    parser.add_argument('--baseline', default=str(Path(__file__).with_name('baseline.json')))
    args = parser.parse_args()
    report = evaluate(json.loads(Path(args.dataset).read_text()))
    baseline = json.loads(Path(args.baseline).read_text())
    old = {r['id']: r for r in baseline['cases']}
    report['regressions'] = [r['id'] for r in report['cases'] if
                             r['id'] in old and
                             ((old[r['id']]['retrieval_pass'] and not r['retrieval_pass']) or
                              (old[r['id']]['support_check_pass'] and not r['support_check_pass']))]
    report['removed_cases'] = sorted(set(old) - {r['id'] for r in report['cases']})
    report['hit_rate_delta'] = report['retrieval_hit_rate'] - baseline['retrieval_hit_rate']
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'cases'}, indent=2))
    return 0 if report['contract_pass'] and not report['regressions'] and not report['removed_cases'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
