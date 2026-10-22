import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_research as r


class TestResearch(unittest.TestCase):
    def test_form_parser_and_empty_response(self):
        fields = r.parse_body('### Target buyer\n\nWestern wear\n\n### Region\n\nUS\n\n### Production constraints\n\n_No response_')
        self.assertEqual(fields['buyer'], 'Western wear')
        self.assertEqual(fields['region'], 'US')
        self.assertEqual(fields['constraints'], '')

    def test_safe_urls_refuse_etsy_and_injection(self):
        self.assertIsNone(r.safe_url('https://www.etsy.com/listing/123'))
        self.assertIsNone(r.safe_url('javascript:alert(1)'))
        self.assertIsNone(r.safe_url('https://attacker:pw@example.com/'))
        self.assertEqual(r.safe_url('https://help.erank.com/blog/'), 'https://help.erank.com/blog/')

    def test_normalization_does_not_invent_direct_evidence(self):
        issue = {'number': 42, 'name': 'Hand-tooled leather patches', 'issue_url': 'https://github.com/u/r/issues/42', 'body': ''}
        raw = {'summary': 'Preliminary signals only', 'opportunities': [
            {'concept': 'Hand-tooled patch', 'research_priority': 93,
             'source_urls': ['https://not-retrieved.example/article']},
            {'concept': 'Western ornaments', 'research_priority': 85,
             'source_urls': ['https://help.erank.com/blog/']},
        ]}
        report = r.normalize_report(raw, {'https://help.erank.com/blog/'}, issue, '2026-10-21T00:00:00+00:00')
        self.assertEqual(report['opportunities'][0]['evidence_level'], 'D')
        self.assertEqual(report['opportunities'][0]['research_priority'], 65)
        self.assertEqual(report['opportunities'][1]['evidence_level'], 'C')
        self.assertEqual(report['opportunities'][1]['source_urls'], ['https://help.erank.com/blog/'])
        self.assertNotIn('searches', report)

    def test_web_tool_provenance(self):
        response = SimpleNamespace(output=[SimpleNamespace(action=SimpleNamespace(sources=[
            SimpleNamespace(url='https://help.erank.com/blog/'),
            SimpleNamespace(url='https://www.etsy.com/search?q=leather')]),
            content=[SimpleNamespace(annotations=[SimpleNamespace(url='https://example.org/report')])])])
        self.assertEqual(r.find_retrieved_urls(response), {'https://help.erank.com/blog/', 'https://example.org/report'})

    def test_only_owner_open_niches_and_no_pull_requests(self):
        data = [
            {'number': 1,'state': 'open','title': '[Niche] Leather patches','user': {'login': 'user'},'body': '','html_url':'https://github.com/user/repo/issues/1'},
            {'number': 2,'state': 'open','title': '[Niche] False','user': {'login': 'stranger'},'body': ''},
            {'number': 3,'state': 'closed','title': '[Niche] Closed','user': {'login': 'user'},'body': ''},
            {'number': 4,'state': 'open','title': '[Niche] This is a PR','user': {'login': 'user'},'body': '', 'pull_request': {}},
        ]
        with patch.object(r, 'get_json', return_value=data):
            self.assertEqual([x['number'] for x in r.list_niches('user/repo', 'token')], [1])

    def test_close_updates_feed_without_paid_research(self):
        old_data = {'niches': [{'issue_number': 1, 'niche': 'Old niche'}, {'issue_number': 2, 'niche': 'Still open'}]}
        with tempfile.TemporaryDirectory() as tmp:
            feed = Path(tmp)/'latest.json'
            with patch.object(r, 'LATEST', feed), patch.object(r, 'DATA', Path(tmp)), \
                 patch.object(r, 'get_latest', return_value=old_data), \
                 patch.object(r, 'list_niches', return_value=[{'number': 2, 'name': 'Still open', 'body':'', 'issue_url':''}]), \
                 patch.dict(os.environ, {'GITHUB_REPOSITORY':'user/repo', 'GH_TOKEN':'token',
                                         'GITHUB_EVENT_NAME':'issues', 'GITHUB_EVENT_PATH':''}, clear=True):
                # For closed issue #1, event identifies a number with no open targets.
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as ev:
                    json.dump({'issue': {'number': 1}}, ev); ev.flush()
                    os.environ['GITHUB_EVENT_PATH'] = ev.name
                    r.run()
                self.assertEqual([x['issue_number'] for x in json.loads(feed.read_text())['niches']], [2])


if __name__=='__main__':
    unittest.main()
