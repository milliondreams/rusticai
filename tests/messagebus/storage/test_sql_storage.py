import unittest

from .storage_backend_base_test import AbstractTests


class TestSQLBasedStorage(AbstractTests.TestStorageBackendABC, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

    def get_storage_config(self) -> dict:
        return {'message_bus': {'storage': {'type': 'SQL', 'connection_string': 'sqlite://'}}}

    def tearDown(self):
        # Close the connection after each test
        self.get_storage_backend().engine.dispose()
