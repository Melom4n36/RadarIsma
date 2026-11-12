"""Pruebas sin red ni credenciales."""
import base64
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import collect


class CollectorTests(unittest.TestCase):
    def test_exactly_nineteen_unique_communities(self):
        self.assertEqual(len(collect.SUBREDDITS), 19)
        self.assertEqual(len({s.casefold() for s in collect.SUBREDDITS}), 19)
        self.assertIn('ArtificialInteligence', collect.SUBREDDITS)
        self.assertIn('claude', collect.SUBREDDITS)
        self.assertIn('ClaudeAI', collect.SUBREDDITS)

    def test_oauth_request_uses_client_credentials(self):
        with patch.object(collect, 'request', return_value={'access_token': 'dummy'}) as req:
            self.assertEqual(collect.token('id', 'secret', 'agent'), 'dummy')
            args, kwargs = req.call_args
            self.assertIn('access_token', args[0])
            self.assertEqual(args[1]['User-Agent'], 'agent')
            self.assertEqual(args[2], b'grant_type=client_credentials')
            self.assertEqual(args[1]['Authorization'], 'Basic ' + base64.b64encode(b'id:secret').decode())

    def test_comment_filtering(self):
        post = {'permalink': '/r/sysadmin/comments/abc/example/'}
        listing = [{}, {'data': {'children': [
            {'kind': 't1', 'data': {'id': 'a', 'body': 'Useful comment', 'permalink': '/r/sysadmin/comments/abc/a/', 'score': 2}},
            {'kind': 't1', 'data': {'id': 'b', 'body': '[deleted]'}},
            {'kind': 'more', 'data': {}}
        ]}}]
        with patch.object(collect, 'get', return_value=listing):
            comments = collect.comments_for(post, {}, 10)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]['body'], 'Useful comment')
        self.assertTrue(comments[0]['permalink'].startswith('https://www.reddit.com/'))


if __name__ == '__main__':
    unittest.main()
