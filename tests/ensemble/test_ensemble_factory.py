import tempfile
import unittest

from fakeredis import FakeStrictRedis

from rustic_ai.ensemble.storage.ensemble_factory import EnsembleStorageFactory
from rustic_ai.ensemble.storage.file_based_storage import FileEnsembleStorage
from rustic_ai.ensemble.storage.in_memory_storage import InMemoryEnsembleStorage
from rustic_ai.ensemble.storage.redis_storage import RedisEnsembleStorage
from rustic_ai.ensemble.storage.sql_storage import SqlEnsembleStorage


class TestEnsembleStorageFactory(unittest.TestCase):
    # Tests that an InMemoryEnsembleStorage instance is created when
    # the config specifies 'IN_MEMORY' storage type
    def test_in_memory_storage_creation(self):
        config = {'ensemble': {'storage': {'type': 'MEMORY'}}}
        storage = EnsembleStorageFactory.from_config(config)
        self.assertIsInstance(storage, InMemoryEnsembleStorage)

    # Tests that a FileEnsembleStorage instance is created when the config specifies
    # 'FILE_BASED' storage type and a valid file path is provided
    def test_file_storage_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'ensemble': {'storage': {'type': 'FILE', 'file_path': tmpdir}}}
            storage = EnsembleStorageFactory.from_config(config)
            self.assertIsInstance(storage, FileEnsembleStorage)

    # Tests that a SqlEnsembleStorage instance is created when the config specifies
    # 'SQL' storage type and a valid connection string is provided
    def test_sql_storage_creation(self):
        config = {'ensemble': {'storage': {'type': 'SQL', 'connection_string': 'sqlite:///:memory:'}}}
        storage = EnsembleStorageFactory.from_config(config)
        self.assertIsInstance(storage, SqlEnsembleStorage)

    # Tests that a RedisEnsembleStorage instance is created when the config specifies
    # 'REDIS' storage type and a valid connection string is provided, and fake Redis is used
    def test_redis_storage_creation_with_fake_redis(self):
        config = {
            'ensemble': {
                'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379', 'fake_redis': True}
            }
        }
        storage = EnsembleStorageFactory.from_config(config)
        self.assertIsInstance(storage, RedisEnsembleStorage)

    # Tests that a RedisEnsembleStorage instance is created when the config specifies
    # 'REDIS' storage type and a valid connection string is provided, and fake Redis is not used
    def test_redis_storage_creation_without_fake_redis(self):
        config = {'ensemble': {'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379'}}}
        storage = EnsembleStorageFactory.from_config(config)
        self.assertIsInstance(storage, RedisEnsembleStorage)

    # Tests that an exception is raised when the config is empty or does not specify a valid storage type
    def test_invalid_config(self):
        with self.assertRaises(Exception):
            EnsembleStorageFactory.from_config({})
        with self.assertRaises(Exception):
            EnsembleStorageFactory.from_config({'ensemble': {'storage': {'type': 'INVALID'}}})

    # Tests that an exception is raised when creating a FileEnsembleStorage instance with an invalid file path
    def test_invalid_file_path(self):
        config = {'ensemble': {'storage': {'type': 'FILE_BASED', 'file_path': 'invalid/path'}}}
        with self.assertRaises(Exception):
            EnsembleStorageFactory.from_config(config)

    # Tests that an exception is raised when creating a SqlEnsembleStorage instance with an invalid connection string
    def test_invalid_connection_string(self):
        config = {'ensemble': {'storage': {'type': 'SQL', 'connection_string': 'invalid_connection_string'}}}
        with self.assertRaises(Exception):
            EnsembleStorageFactory.from_config(config)

    # Tests that a RedisEnsembleStorage instance is created with fake Redis when specified in the config
    def test_fake_redis(self):
        config = {
            'ensemble': {
                'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379', 'fake_redis': True}
            }
        }
        storage = EnsembleStorageFactory.from_config(config)
        self.assertIsInstance(storage, RedisEnsembleStorage)
        self.assertIsInstance(storage.redis, FakeStrictRedis)
