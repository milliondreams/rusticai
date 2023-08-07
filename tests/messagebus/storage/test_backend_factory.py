import tempfile
import unittest

from rustic_ai.messagebus.storage.backend_factory import StorageBackendFactory
from rustic_ai.messagebus.storage.file_based_storage import FileBasedStorage
from rustic_ai.messagebus.storage.in_memory_storage import InMemoryStorage
from rustic_ai.messagebus.storage.redis_storage import RedisStorage
from rustic_ai.messagebus.storage.sql_storage import SQLStorage


class TestStorageBackendFactory(unittest.TestCase):
    # Tests that the 'from_config' method of the 'StorageBackendFactory' class
    # returns an instance of 'InMemoryStorage' when the storage type is 'MEMORY'.
    def test_from_config_returns_in_memory_storage_when_type_is_in_memory(self):
        config = {'message_bus': {'storage': {'type': 'MEMORY'}}}
        storage_backend = StorageBackendFactory.from_config(config)
        self.assertIsInstance(storage_backend, InMemoryStorage)

    # Tests that the 'from_config' method returns an instance of 'FileBasedStorage' when
    # the storage type is 'FILE'
    def test_file_based_storage_instance_returned(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = {'message_bus': {'storage': {'type': 'FILE', 'file_path': tmp_dir}}}
            storage_backend = StorageBackendFactory.from_config(config)
            self.assertIsInstance(storage_backend, FileBasedStorage)

    # Tests that the 'from_config' method returns an instance of 'SQLStorage' when the storage type is 'SQL'
    def test_from_config_returns_SQLStorage_when_storage_type_is_SQL(self):
        config = {'message_bus': {'storage': {'type': 'SQL', 'connection_string': 'sqlite://'}}}
        storage_backend = StorageBackendFactory.from_config(config)
        self.assertIsInstance(storage_backend, SQLStorage)

    # Tests that the 'from_config' method returns an instance of 'RedisStorage' when the storage type is 'REDIS'
    def test_redis_storage_instance_returned(self):
        config = {'message_bus': {'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379/0'}}}
        storage_backend = StorageBackendFactory.from_config(config)
        self.assertIsInstance(storage_backend, RedisStorage)

    # Tests that a ValueError is raised when an unrecognized storage type is provided in the config
    def test_unrecognized_storage_type(self):
        with self.assertRaises(ValueError):
            StorageBackendFactory.from_config({'message_bus': {'storage': {'type': 'unknown'}}})

    # Tests that a KeyError is raised when the 'storage' key is missing from the config
    def test_missing_storage_key(self):
        with self.assertRaises(KeyError):
            StorageBackendFactory.from_config({})

    # Tests that a KeyError is raised when the 'type' key is missing from the 'storage' config
    def test_missing_type_key(self):
        config = {'message_bus': {'storage': {}}}
        with self.assertRaises(KeyError):
            StorageBackendFactory.from_config(config)

    # Tests that a KeyError is raised when the 'file_path' key is missing from the 'storage'
    # config for 'FILE' storage type
    def test_missing_file_path_key(self):
        config = {'message_bus': {'storage': {'type': 'FILE'}}}
        with self.assertRaises(KeyError):
            StorageBackendFactory.from_config(config)

    # Tests that a KeyError is raised when the 'connection_string' key is missing from the 'storage'
    # config for 'SQL' or 'REDIS' storage type
    def test_missing_connection_string_key(self):
        config = {'message_bus': {'storage': {'type': 'SQL'}}}
        with self.assertRaises(KeyError):
            StorageBackendFactory.from_config(config)

        config = {'message_bus': {'storage': {'type': 'REDIS'}}}
        with self.assertRaises(KeyError):
            StorageBackendFactory.from_config(config)

    # Tests that the method 'from_config' returns the same instance of 'InMemoryStorage' when called multiple times
    def test_return_same_instance_of_InMemoryStorage_when_called_multiple_times(self):
        config = {'message_bus': {'storage': {'type': 'MEMORY'}}}
        storage_backend_1 = StorageBackendFactory.from_config(config)
        storage_backend_2 = StorageBackendFactory.from_config(config)
        self.assertIs(storage_backend_1, storage_backend_2)

    # Tests that the method 'from_config' returns different instances of 'FileBasedStorage'
    # when called with different file paths
    def test_different_file_paths(self):
        config = {'message_bus': {'storage': {'type': 'FILE', 'file_path': '/tmp/test1'}}}
        storage1 = StorageBackendFactory.from_config(config)

        config = {'message_bus': {'storage': {'type': 'FILE', 'file_path': '/tmp/test2'}}}
        storage2 = StorageBackendFactory.from_config(config)

        self.assertIsInstance(storage1, FileBasedStorage)
        self.assertIsInstance(storage2, FileBasedStorage)
        self.assertNotEqual(storage1, storage2)

    # Tests that the method 'from_config' returns different instances of 'RedisStorage'
    # when called with different connection strings
    def test_redis_storage_instances_with_different_connection_strings(self):
        config = {'message_bus': {'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379/0'}}}
        redis_storage_1 = StorageBackendFactory.from_config(config)

        config = {'message_bus': {'storage': {'type': 'REDIS', 'connection_string': 'redis://localhost:6379/1'}}}
        redis_storage_2 = StorageBackendFactory.from_config(config)

        self.assertNotEqual(redis_storage_1, redis_storage_2)
