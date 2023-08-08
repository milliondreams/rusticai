from typing import TYPE_CHECKING, Dict, List, Optional

import shortuuid

from .message import Message
from .routing import BroadcastRoutingPolicy, RoutingPolicy
from .storage import InMemoryStorage, StorageBackend
from .utils import GemstoneGenerator, Priority

if TYPE_CHECKING:  # pragma: no cover
    from .client.client import Client


class MessageBus:
    """
    MessageBus is a central component responsible for managing clients, sending messages,
    and handling routing and storage policies.
    """

    def __init__(
        self,
        id: Optional[str] = None,
        machine_id: int = 1,
        storage_backend: Optional[StorageBackend] = None,
        routing_policy: Optional[RoutingPolicy] = None,
    ):
        """
        Initialize the MessageBus with the given storage backend and routing policy.
        If no storage backend is provided, InMemoryStorage will be used.
        If no routing policy is provided, BroadcastRoutingPolicy will be used.

        :param storage_backend: Storage backend to use for message storage
        :param routing_policy: Routing policy to use for message delivery
        """
        self.id = id if id else shortuuid.uuid()
        self.clients: Dict[str, 'Client'] = {}
        self.id_generator: GemstoneGenerator = GemstoneGenerator(machine_id)
        self.storage: StorageBackend = storage_backend or InMemoryStorage()
        self.routing_policy: RoutingPolicy = routing_policy or BroadcastRoutingPolicy()
        self.listeners: List[str] = []

    def generate_message_id(self, priority: Priority) -> int:
        """
        Generate a new message ID.

        :return: A new message ID
        """
        return self.id_generator.get_id(priority).to_int()

    def register_client(self, client: 'Client', listener: bool = False) -> None:
        """
        Register a new client with the MessageBus.

        :param client: The client to register
        """
        self.clients[client.client_id] = client
        self.storage.create_inbox(self.id, client.client_id)

        if listener:
            self.listeners.append(client.client_id)

    def unregister_client(self, client: 'Client') -> None:
        """
        Unregister a client from the MessageBus.

        :param client: The client to unregister
        """
        self.clients.pop(client.client_id, None)
        self.storage.remove_inbox(self.id, client.client_id)
        if client.client_id in self.listeners:
            self.listeners.remove(client.client_id)

    def send_message(self, message: Message) -> None:
        """
        Send a message to the recipients determined by the routing policy.

        :param message: The message to send
        """

        # Check if recipients are valid
        if set(message.recipients).difference(self.clients.keys()):
            raise ValueError("Invalid recipient(s) specified")

        # Get the recipients from the routing policy
        if message.recipients:
            recipients = message.recipients
        else:
            recipients = self.routing_policy.get_recipients(message, self.clients)

        # Add listeners to the list of recipients is listeners is not empty
        if self.listeners:
            recipients.extend(self.listeners)

        recipients = list(set(recipients))

        # Add message to the recipient's inbox
        for recipient_id in recipients:
            self.storage.add_message_to_inbox(self.id, recipient_id, message)

        # Notify the recipients of new messages
        for recipient_id in recipients:
            if recipient_id in self.clients:
                self.clients[recipient_id].notify_new_message()

    def get_next_unread_message(self, client_id: str, last_read_message_id: int) -> Optional[Message]:
        """
        Get the next unread message for the given client ID, starting from the last read message ID.

        :param client_id: The client ID requesting the next unread message
        :param last_read_message_id: The last read message ID for the client
        :return: The next unread message if available, otherwise None
        """
        return self.storage.get_next_unread_message(self.id, client_id, last_read_message_id)

    def remove_received_message(self, sender_id: str, recipient_ids: List[str], message_id: int) -> None:
        """
        Remove a sent message from the listed recipient's inbox.

        :param sender_id: The sender's client ID
        :param recipient_ids: The recipient's client ID, should not be empty.
            If the first element is '*', the message will be removed from all recipients.
        :param message_id: The message ID to remove
        """
        assert recipient_ids, ValueError('recipient_ids must not be empty')

        if recipient_ids[0] == '*':
            self.storage.remove_received_message(self.id, sender_id, list(self.clients.keys()), message_id)
        else:
            self.storage.remove_received_message(self.id, sender_id, recipient_ids, message_id)

    def set_routing_policy(self, routing_policy: RoutingPolicy) -> None:
        """
        Set a new routing policy for the MessageBus.

        :param routing_policy: The new routing policy to use
        """
        self.routing_policy = routing_policy
