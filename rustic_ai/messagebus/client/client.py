from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..message import JSON, Message
from ..message_bus import MessageBus
from ..utils import Priority


class Client(ABC):
    """
    An abstract base class for a client that communicates via the message bus.
    """

    def __init__(self, client_id: str, message_bus: MessageBus, listener: bool = False):
        """
        Initialize the client with a unique ID and a reference to the message bus.

        :param client_id: Unique identifier for this client
        :param message_bus: Reference to the message bus instance
        """
        self.client_id: str = client_id
        self.message_bus: MessageBus = message_bus
        self.last_read_message_id: int = 0

        self.message_bus.register_client(self, listener=listener)

    def __del__(self):  # pragma: no cover
        if hasattr(self, 'message_bus'):
            self.message_bus.unregister_client(self)

    def send_message(
        self, content: JSON, recipients: Optional[List[str]] = None, priority: Priority = Priority.NORMAL
    ) -> Message:
        """
        Send a message through the message bus.

        :param content: The content of the message to send
        :param recipients: Optional list of recipient client IDs
        :param priority: Optional priority level of the message
        """
        assert isinstance(content, Dict)
        message_id = self.message_bus.generate_message_id(priority)
        message = Message(message_id, sender=self.client_id, content=content, recipients=recipients, priority=priority)
        self.message_bus.send_message(message)
        return message

    @abstractmethod
    def get_next_unread_message(self) -> Optional[Message]:
        """
        Abstract method to fetch the next unread message for this client.

        :return: The next unread message, if one exists
        """
        pass  # pragma: no cover

    @abstractmethod
    def notify_new_message(self) -> None:
        """
        Abstract method to notify the client of a new message.

        """
        pass  # pragma: no cover

    def remove_sent_message(self, recipient_ids: List[str], message_id: int) -> None:
        """
        Remove a sent message from the message bus.

        :param recipient_ids: The IDs of the recipients of the message
        :param message_id: The ID of the message to remove
        """
        self.message_bus.remove_received_message(self.client_id, recipient_ids, message_id)
