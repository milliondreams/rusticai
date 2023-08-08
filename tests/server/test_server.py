import unittest

from fastapi.testclient import TestClient

from rustic_ai import __version__ as version


class TestServer(unittest.TestCase):
    def setUp(self):
        from rustic_ai.server.main import app

        self.app = app
        self.client = TestClient(self.app)

    # Tests that the function returns a JSON object with a 'message' key
    def test_returns_message_key(self):
        response = self.client.get('/')
        assert 'message' in response.json().keys()

    # Test health check returns a JSON with 'message' value 'OK'
    def test_health_check(self):
        response = self.client.get('/health')
        assert response.json()['message'] == 'OK'

    # Test version check returns a JSON with 'version' of the package
    def test_version_check(self):
        response = self.client.get('/version')
        assert response.json()['version'] == version
