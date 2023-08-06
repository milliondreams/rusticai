import unittest

from rustic_ai.ensemble.storage import SqlEnsembleStorage

from .ensemble_storage_base_test import AbstractTests


class TestSqlEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    def get_storage(self):
        return SqlEnsembleStorage("sqlite://")

    def tearDown(self):
        super().tearDown()
        self.storage.close_connection()
