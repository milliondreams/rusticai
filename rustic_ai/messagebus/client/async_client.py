import asyncio
from typing import Optional

from ..message import Message
from ..message_bus import MessageBus
from .client import Client


class AsyncClient(Client):
    """
    WARNING: WIP DO NOT USE
    An asynchronous implementation of the Client, using asyncio's Queue to manage messages.
    """

    def __init__(self, client_id: str, message_bus: MessageBus, listener: bool = False) -> None:
        """
        Initialize the asynchronous client with a unique ID and a reference to the message bus.

        :param client_id: Unique identifier for this client
        :param message_bus: Reference to the message bus instance
        """
        super().__init__(client_id, message_bus, listener)

    def get_next_unread_message(self) -> Optional[Message]:
        """
        Synchronously get the next unread message from the queue for this client.
        :return: The next unread message, if one exists
        """
        message = self.message_bus.get_next_unread_message(self.client_id, self.last_read_message_id)
        return message

    async def async_get_next_unread_message(self) -> asyncio.Future[Optional[Message]]:
        """
        Asynchronously get the next unread message from the queue for this client.

        :return: The next unread message, if one exists
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_next_unread_message)  # type: ignore

    def notify_new_message(self) -> None:
        """
        Schedule a new task to fetch and process the new message asynchronously.
        """
        pass
