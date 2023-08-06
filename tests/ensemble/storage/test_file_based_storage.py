import tempfile
import unittest

from rustic_ai.ensemble.storage import FileEnsembleStorage

from .ensemble_storage_base_test import AbstractTests


class TestFileEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    """
    A test case for the FileEnsembleStorage class.

    This class extends the TestEnsembleStorage class and provides an implementation of the
    `get_storage()` method that returns an instance of the FileEnsembleStorage class.
    """

    def get_storage(self):
        self.temp_dir = tempfile.mkdtemp()
        return FileEnsembleStorage(self.temp_dir)


if __name__ == '__main__':
    unittest.main()
