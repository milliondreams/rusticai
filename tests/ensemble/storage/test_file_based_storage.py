import tempfile
import unittest

from .ensemble_storage_base_test import AbstractTests


class TestFileEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    """
    A test case for the FileEnsembleStorage class.

    This class extends the TestEnsembleStorage class and provides an implementation of the
    `get_storage_config()` method that returns an instance of the FileEnsembleStorage class.
    """

    def get_storage_config(self) -> dict:
        self.temp_dir = tempfile.mkdtemp()
        return {'ensemble': {'storage': {'type': 'FILE', 'file_path': self.temp_dir}}}


if __name__ == '__main__':
    unittest.main()
