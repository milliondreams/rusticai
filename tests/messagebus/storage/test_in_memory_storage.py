import unittest

from .storage_backend_base_test import AbstractTests


class TestInMemoryStorage(AbstractTests.TestStorageBackendABC, unittest.TestCase):
    def get_storage_config(self) -> dict:
        return {'message_bus': {'storage': {'type': 'MEMORY'}}}


if __name__ == '__main__':
    unittest.main()
