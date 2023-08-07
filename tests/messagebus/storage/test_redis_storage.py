import unittest

from .storage_backend_base_test import AbstractTests


class TestRedisStorage(AbstractTests.TestStorageBackendABC, unittest.TestCase):
    def get_storage_config(self) -> dict:
        return {
            'message_bus': {
                'storage': {'type': 'REDIS', 'fake_redis': True, 'connection_string': 'redis://localhost:6379'}
            }
        }

    def tearDown(self):
        # Clean up fake Redis database after each test
        self.storage.redis.flushall()
        self.storage.redis.close()
