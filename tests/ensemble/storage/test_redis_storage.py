import unittest

from .ensemble_storage_base_test import AbstractTests


class TestRedisEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    def get_storage_config(self) -> dict:
        return {
            'ensemble': {
                'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379', 'fake_redis': True}
            }
        }

    def tearDown(self):
        self.storage.redis.flushall()
        self.storage.redis.close()
