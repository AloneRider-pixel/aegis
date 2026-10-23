"""Regression tests for the evaluator itself, using synthetic fixtures only."""
import json
from pathlib import Path
import unittest
from rag_eval import evaluate, retrieve, supported


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path(__file__).with_name('golden.json').read_text())

    def test_golden_contract(self):
        self.assertTrue(evaluate(self.data)['contract_pass'])

    def test_lost_document_is_regression(self):
        self.data['documents'] = self.data['documents'][1:]
        result = evaluate(self.data)
        self.assertFalse(result['contract_pass'])
        self.assertLess(result['retrieval_hit_rate'], 1)

    def test_unknown_citation_fails(self):
        self.assertFalse(supported('hello', ['unknown'], self.data['documents']))

    def test_empty_answer_is_not_grounded(self):
        self.assertFalse(supported('', ['pool'], self.data['documents']))

    def test_retrieval_case_insensitive(self):
        self.assertEqual(retrieve('POOL EXHAUSTION', self.data['documents'])[0]['id'], 'pool')

    def test_top_k_is_applied(self):
        self.assertEqual(len(retrieve('', self.data['documents'], 2)), 2)

    def test_no_citation_cannot_pass(self):
        self.assertFalse(supported(self.data['documents'][0]['content'], [], self.data['documents']))

    def test_invented_claim_cannot_pass(self):
        self.assertFalse(supported('Do the dangerous thing.', ['pool'], self.data['documents']))


if __name__ == '__main__':
    unittest.main()
