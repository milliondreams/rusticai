import unittest

from .ensemble_storage_base_test import AbstractTests


class TestSqlEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    def get_storage_config(self) -> dict:
        return {'ensemble': {'storage': {'type': 'SQL', 'connection_string': 'sqlite:///:memory:'}}}

    def tearDown(self):
        super().tearDown()
        self.storage.close_connection()
