import logging
from typing import Callable, Optional

from ..message import Message
from ..message_bus import MessageBus
from .client import Client


class CallbackClient(Client):
    """
    A client implementation that uses a callback function to process incoming messages.
    """

    def __init__(
        self,
        client_id: str,
        message_bus: MessageBus,
        message_callback: Callable[[Message], None],
        listener: bool = False,
    ) -> None:
        """
        Initialize the callback client with a unique ID, a reference to the message bus, and a callback function.

        :param client_id: Unique identifier for this client
        :param message_bus: Reference to the message bus instance
        :param message_callback: The callback function to be triggered when a new message arrives
        """
        super().__init__(client_id, message_bus, listener)
        if not callable(message_callback):
            raise TypeError('message_callback must be a callable function')
        self.message_callback: Callable[[Message], None] = message_callback
        self.logger = logging.getLogger(__name__)

    def get_next_unread_message(self) -> Optional[Message]:
        """
        Fetch the next unread message for this client.

        :return: The next unread message, if one exists
        """
        message = self.message_bus.get_next_unread_message(self.client_id, self.last_read_message_id)

        if message is not None:
            self.last_read_message_id = message.id

        return message

    def handle_message(self, message: Message) -> None:
        """
        Handle the message with the callback function.

        :param message: The message to handle
        """
        self.message_callback(message)

    def notify_new_message(self) -> None:
        """
        Fetch the new message and handle it with the callback function.
        """
        try:
            message = self.get_next_unread_message()
            if message is not None:
                self.handle_message(message)
        except Exception as e:
            self.logger.error('Error handling message: %s', e)
            pass

    def process_all_unread_messages(self) -> None:
        """
        Fetch and handle all unread messages for this client until now.
        """
        message = self.get_next_unread_message()
        while message is not None:
            self.handle_message(message)
            message = self.get_next_unread_message()
