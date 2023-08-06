import unittest

from rustic_ai.ensemble.storage import InMemoryEnsembleStorage

from .ensemble_storage_base_test import AbstractTests


class TestInMemoryEnsembleStorage(AbstractTests.TestEnsembleStorageABC, unittest.TestCase):
    """
    A test case for the InMemoryEnsembleStorage class.

    This class extends the TestEnsembleStorage class and provides an implementation of the `get_storage()` method that
    returns an instance of the InMemoryEnsembleStorage class.
    """

    def get_storage(self):
        """
        Get an instance of the InMemoryEnsembleStorage class.

        :return: An instance of the InMemoryEnsembleStorage class
        """
        return InMemoryEnsembleStorage()


if __name__ == '__main__':
    unittest.main()
