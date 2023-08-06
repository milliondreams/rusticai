import unittest

from fastapi.testclient import TestClient


class TestServer(unittest.TestCase):
    def setUp(self):
        from rustic_ai.server.main import app

        self.app = app
        self.client = TestClient(self.app)

    # Tests that the function returns a JSON object with a 'message' key
    def test_returns_message_key(self):
        response = self.client.get('/')
        assert 'message' in response.json().keys()
