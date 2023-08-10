import time
import unittest

import pytest
from fastapi.testclient import TestClient

from rustic_ai import __version__ as version


@pytest.fixture
def test_http_server(request, httpserver):
    """Attach pytest fixture to all tests that need it."""
    request.cls.httpserver = httpserver


@pytest.mark.usefixtures("test_http_server")
class TestServer(unittest.TestCase):
    def setUp(self):
        from rustic_ai.server.main import app

        self.app = app
        self.client = TestClient(self.app)

    # Tests that the function returns a HTML response
    def test_returns_message_key(self):
        response = self.client.get('/')
        self.assertEquals(200, response.status_code)
        assert 'text/html' in response.headers['content-type']

    # Test health check returns a JSON with 'message' value 'OK'
    def test_health_check(self):
        response = self.client.get('/health')
        assert response.json()['message'] == 'OK'

    # Test version check returns a JSON with 'version' of the package
    def test_version_check(self):
        response = self.client.get('/version')
        assert response.json()['version'] == version

    # Test config check returns a JSON with 'path' and 'config' values
    def test_config_check(self):
        response = self.client.get('/config')
        assert 'path' in response.json()
        assert 'config' in response.json()

    # Test create ensemble returns a JSON with 'ensemble_id' value
    # and the ensemble is added to the ensemble manager
    def test_create_ensemble(self):
        response = self.client.post('/app/ensembles', json={'name': 'test'})
        assert 'id' in response.json()
        assert 'name' in response.json()
        assert response.json()['name'] == 'test'

        fetched_ensemble = self.client.get('/app/ensembles/' + response.json()['id'])
        assert 'id' in fetched_ensemble.json()
        assert 'name' in fetched_ensemble.json()
        assert fetched_ensemble.json()['name'] == 'test'

    # Test get all ensembles
    def test_get_ensembles(self):
        response = self.client.post('/app/ensembles', json={'name': 'test'})
        assert 'id' in response.json()
        assert 'name' in response.json()
        assert response.json()['name'] == 'test'

        response = self.client.get('/app/ensembles')
        assert len(response.json()) > 0

    # Test add member to ensemble
    def test_add_member(self):
        # Test add member and HTTP callback
        calls_recorded = 0

        def callback(r1):
            nonlocal calls_recorded
            calls_recorded += 1
            return "OK"

        self.httpserver.expect_request("/callback1/", method="POST").respond_with_handler(callback)
        self.httpserver.expect_request("/callback2/", method="POST").respond_with_handler(callback)

        # Create ensemble and get its ID
        ensemble = self.client.post('/app/ensembles', json={'name': 'member_test_ensemble'})
        ensemble_id = ensemble.json()['id']

        # Add member to ensemble
        member1 = self.client.post(
            '/app/ensembles/' + ensemble_id + '/members',
            json={'name': 'member1', 'member_type': 'bot', 'callback_url': self.httpserver.url_for("/callback1/")},
        )

        member2 = self.client.post(
            '/app/ensembles/' + ensemble_id + '/members',
            json={'name': 'member2', 'member_type': 'bot', 'callback_url': self.httpserver.url_for("/callback2/")},
        )

        # Check that the member was added to the ensemble
        ensemble_with_members = self.client.get('/app/ensembles/' + ensemble_id)
        ewm_json = ensemble_with_members.json()
        assert len(ewm_json['members']) > 0

        member1_id = member1.json()['id']
        member2_id = member2.json()['id']

        # Send a message to the ensemble
        message_json = {'sender': member1_id, 'content': {'message': 'hello'}, 'recipients': [member2_id]}
        message = self.client.post('/app/ensembles/' + ensemble_id + '/messages', json=message_json)

        # Wait for the message to be processed
        time.sleep(2)

        # Assert correct message response
        response_json = message.json()
        assert response_json['sender'] == member1_id
        assert response_json['content']['message'] == 'hello'
        assert response_json['recipients'][0] == member2_id
        assert response_json['priority'] == 4

        self.httpserver.check_assertions()

        assert calls_recorded == 1


if __name__ == '__main__':
    unittest.main()
