import os
import tempfile
import unittest

from .storage_backend_base_test import AbstractTests


class TestFileBasedStorage(AbstractTests.TestStorageBackendABC, unittest.TestCase):
    def get_storage_config(self) -> dict:
        self.temp_dir = tempfile.mkdtemp()
        return {'message_bus': {'storage': {'type': 'FILE', 'file_path': self.temp_dir}}}

    def tearDown(self):
        # Cleanup the temporary directory after each test
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)
