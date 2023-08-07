import time
from abc import ABC, abstractmethod

from rustic_ai.messagebus import Message, StorageBackend
from rustic_ai.messagebus.storage.backend_factory import StorageBackendFactory
from rustic_ai.messagebus.utils import GemstoneGenerator, Priority


class AbstractTests(object):
    class TestStorageBackendABC(ABC):
        @abstractmethod
        def get_storage_config(self) -> dict:
            pass

        def get_storage_backend(self) -> StorageBackend:
            if '_storage' not in self.__dict__:
                self._storage = StorageBackendFactory.from_config(self.get_storage_config())
            return self._storage

        def setUp(self):
            self.storage = self.get_storage_backend()
            self.id_generator = GemstoneGenerator(1)

        def _get_id(self, priority: Priority) -> int:
            return self.id_generator.get_id(priority).to_int()

        def test_create_and_remove_inbox(self):
            self.storage.create_inbox("message_bus_1", "test_client")
            self.storage.add_message_to_inbox(
                "message_bus_1",
                "test_client",
                Message(self._get_id(Priority.NORMAL), "test_client", {"content": "Hello!"}),
            )
            self.assertIsNotNone(self.storage.get_next_unread_message("message_bus_1", "test_client", 0))
            self.storage.remove_inbox("message_bus_1", "test_client")
            self.assertIsNone(self.storage.get_next_unread_message("message_bus_1", "test_client", 0))

        def test_add_and_get_message(self):
            self.storage.create_inbox("message_bus_1", "test_client")
            msg = Message(self._get_id(Priority.NORMAL), "test_client", {"content": "Hello!"})
            self.storage.add_message_to_inbox("message_bus_1", "test_client", msg)
            retrieved_msg = self.storage.get_next_unread_message("message_bus_1", "test_client", 0)
            self.assertEqual(msg, retrieved_msg)
            self.storage.remove_inbox("message_bus_1", "test_client")

        def test_add_and_get_multiple_messages(self):
            self.storage.create_inbox("message_bus_1", "test_client")
            msg1 = Message(self._get_id(Priority.NORMAL), "test_client", {"content": "Hello!"})
            time.sleep(0.001)
            msg2 = Message(
                self._get_id(Priority.NORMAL),
                "test_client",
                {"content": "Hello again!"},
            )
            self.storage.add_message_to_inbox("message_bus_1", "test_client", msg1)
            self.storage.add_message_to_inbox("message_bus_1", "test_client", msg2)
            retrieved_msg1 = self.storage.get_next_unread_message("message_bus_1", "test_client", 0)
            retrieved_msg2 = self.storage.get_next_unread_message("message_bus_1", "test_client", retrieved_msg1.id)
            retrieved_msg3 = self.storage.get_next_unread_message("message_bus_1", "test_client", retrieved_msg2.id)
            self.assertEqual(msg1, retrieved_msg1)
            self.assertEqual(msg2, retrieved_msg2)
            self.assertIsNone(retrieved_msg3)
            self.storage.remove_inbox("message_bus_1", "test_client")

        def test_remove_received_message(self):
            self.storage.create_inbox("message_bus_2", "test_client_1")
            msg = Message(self._get_id(Priority.NORMAL), "test_client", {"content": "Hello!"})

            self.storage.add_message_to_inbox("message_bus_2", "test_client_1", msg)
            self.storage.remove_received_message("message_bus_2", "test_client", ["test_client_1"], msg.id)

            next_message = self.storage.get_next_unread_message("message_bus_2", "test_client_1", 0)

            self.assertIsNone(next_message)

            self.storage.remove_inbox("message_bus_2", "test_client_1")
