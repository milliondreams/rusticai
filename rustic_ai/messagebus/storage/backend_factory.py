from enum import Enum
from typing import Dict

from fakeredis import FakeStrictRedis

from .file_based_storage import FileBasedStorage
from .in_memory_storage import InMemoryStorage
from .redis_storage import RedisStorage
from .sql_storage import SQLStorage
from .storage import StorageBackend


class StorageBackendType(str, Enum):
    MEMORY = 'MEMORY'
    FILE = 'FILE'
    SQL = 'SQL'
    REDIS = 'REDIS'


class StorageBackendFactory:
    _stores: Dict[str, StorageBackend] = {}

    @staticmethod
    def from_config(config: dict) -> StorageBackend:
        """Create StorageBackend instance from config."""

        storage_config = config['message_bus']['storage']
        storage_type = StorageBackendType(storage_config['type'])
        stores = StorageBackendFactory._stores

        if storage_type == StorageBackendType.MEMORY:
            store_key = StorageBackendType.MEMORY.value
            if store_key not in stores:
                stores[store_key] = InMemoryStorage()
            return stores[store_key]

        elif storage_type == StorageBackendType.FILE:
            file_path = storage_config['file_path']
            store_key = f"{StorageBackendType.MEMORY.value}:{file_path}"
            if store_key not in stores:
                stores[store_key] = FileBasedStorage(file_path)
            return stores[store_key]

        elif storage_type == StorageBackendType.SQL:
            conn = storage_config['connection_string']
            return SQLStorage(conn)

        elif storage_type == StorageBackendType.REDIS:
            conn = storage_config['connection_string']
            store_key = f"{StorageBackendType.REDIS.value}:{conn}"
            fake_redis = storage_config.get('fake_redis', False)

            if store_key not in stores:
                if fake_redis:
                    stores[store_key] = RedisStorage(conn, redis_class=FakeStrictRedis)
                else:
                    stores[store_key] = RedisStorage(conn)

            return stores[store_key]

        else:
            raise ValueError(f'Unknown storage backend type: {storage_type}')
