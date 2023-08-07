from enum import Enum
from typing import Dict

from fakeredis import FakeStrictRedis

from .file_based_storage import FileEnsembleStorage
from .in_memory_storage import InMemoryEnsembleStorage
from .redis_storage import RedisEnsembleStorage
from .sql_storage import SqlEnsembleStorage
from .storage import EnsembleStorage


class EnsembleStorageType(str, Enum):
    MEMORY = 'MEMORY'
    FILE = 'FILE'
    SQL = 'SQL'
    REDIS = 'REDIS'


class EnsembleStorageFactory:
    """Factory class for creating EnsembleStorage instances."""

    _stores: Dict[str, EnsembleStorage] = {}

    @staticmethod
    def from_config(config: dict) -> EnsembleStorage:
        """Create EnsembleStorage instance from config."""
        storage_config = config['ensemble']['storage']
        storage_type = EnsembleStorageType(storage_config['type'])
        stores = EnsembleStorageFactory._stores

        # Instantiate the correct class based on the storage type
        if storage_type == EnsembleStorageType.MEMORY:
            store_key = EnsembleStorageType.MEMORY.value
            if store_key not in stores:
                stores[store_key] = InMemoryEnsembleStorage()
            return stores[store_key]

        elif storage_type == EnsembleStorageType.FILE:
            file_path = storage_config['file_path']
            store_key = f"${EnsembleStorageType.FILE.value}:{file_path}"
            if store_key not in stores:
                stores[store_key] = FileEnsembleStorage(file_path)
            return stores[store_key]

        elif storage_type == EnsembleStorageType.SQL:
            conn = storage_config['connection_string']
            return SqlEnsembleStorage(conn)

        elif storage_type == EnsembleStorageType.REDIS:
            conn = storage_config['connection_string']
            store_key = f"{EnsembleStorageType.REDIS.value}:{conn}"
            fake_redis = storage_config.get('fake_redis', False)

            if store_key not in stores:
                if fake_redis:
                    stores[store_key] = RedisEnsembleStorage(conn, redis_class=FakeStrictRedis)
                else:
                    stores[store_key] = RedisEnsembleStorage(conn)

            return stores[store_key]

        else:
            raise ValueError(f'Unknown ensemble storage type: {storage_type}')
