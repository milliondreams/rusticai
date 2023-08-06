import unittest

import fakeredis

from rustic_ai.ensemble.storage import RedisEnsembleStorage

from .ensemble_storage_base_test import AbstractTests


class TestRedisEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    def get_storage(self) -> RedisEnsembleStorage:
        server = fakeredis.FakeServer()
        return RedisEnsembleStorage(fakeredis.FakeRedis(server=server, charset="utf-8", decode_responses=True))

    def tearDown(self):
        self.storage.redis.flushall()
