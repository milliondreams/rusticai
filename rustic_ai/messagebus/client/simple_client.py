import threading
from typing import Optional

from ..message import Message
from ..message_bus import MessageBus
from .client import Client


class SimpleClient(Client):
    """
    A simple implementation of the Client abstract base class.
    """

    def __init__(self, client_id: str, message_bus: MessageBus) -> None:
        """
        Initialize the simple client with a unique ID and a reference to the message bus.

        :param client_id: Unique identifier for this client
        :param message_bus: Reference to the message bus instance
        """
        super().__init__(client_id, message_bus)
        self.new_message_event = threading.Event()
        self.lock = threading.Lock()

    def get_next_unread_message(self) -> Optional[Message]:
        """
        Fetch the next unread message for this client.

        :return: The next unread message, if one exists
        """
        with self.lock:
            message = self.message_bus.get_next_unread_message(self.client_id, self.last_read_message_id)
            if message is not None:
                self.last_read_message_id = message.id

            return message

    def notify_new_message(self) -> None:
        """
        Notify the client of a new message by setting the new_message_event.
        """
        with self.lock:
            self.new_message_event.set()

    def wait_for_new_message(self, timeout=None):
        """
        Wait for a new message to arrive. If a new message is detected, the method
        will return and the event will be cleared for future messages.

        :param timeout: Optional maximum time to wait for a new message
        """
        self.new_message_event.wait(timeout)  # pragma: no cover
        self.new_message_event.clear()  # pragma: no cover
