import unittest

from rustic_ai.messagebus import BroadcastRoutingPolicy, InMemoryStorage, MessageBus, SimpleClient


class TestMessageBus(unittest.TestCase):
    def setUp(self):
        self.message_bus = MessageBus(
            machine_id=1, storage_backend=InMemoryStorage(), routing_policy=BroadcastRoutingPolicy()
        )
        self.client_1 = SimpleClient('client_1', self.message_bus)
        self.client_2 = SimpleClient('client_2', self.message_bus)
        self.client_3 = SimpleClient('client_3', self.message_bus)

    def test_send_message(self):
        message = self.client_1.send_message({"data": "Hello"})

        # Since we're using a BroadcastRoutingPolicy, the message should be sent to all clients, except the sender
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_1']), 0)
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_2']), 1)
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_3']), 1)

        # The message should be the same as the one sent
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['client_2'][0].content, message.content)
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['client_3'][0].content, message.content)

        # The message should have the correct sender and id
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['client_2'][0].sender, 'client_1')
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['client_3'][0].sender, 'client_1')
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['client_2'][0].id, message.id)
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['client_3'][0].id, message.id)

    def test_remove_received_message(self):
        message = self.client_1.send_message({"data": "Hello"}, ['client_2', 'client_3'])

        self.message_bus.remove_received_message('client_1', ['client_2'], message.id)

        # The message should have been removed from the inbox of client_2
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_2']), 0)

        # The message should still be in the inbox of client_3
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_3']), 1)

    # Test remove received message with multiple recipients
    def test_remove_received_message_multiple_recipients(self):
        message = self.client_1.send_message({"data": "Hello"}, ['client_2', 'client_3'])

        self.message_bus.remove_received_message('client_1', ['client_2', 'client_3'], message.id)

        # The message should have been removed from the inbox of client_2 and client_3
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_2']), 0)
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_3']), 0)

    # Test remove received message with wildcard recipient
    def test_remove_received_message_wildcard_recipient(self):
        message = self.client_1.send_message({"data": "Hello"}, ['client_2', 'client_3'])

        self.message_bus.remove_received_message('client_1', ['*'], message.id)

        # The message should have been removed from the inbox of client_2 and client_3
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_2']), 0)
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['client_3']), 0)

    # Test all messages are delivered clients registered as listeners
    def test_all_messages_delivered(self):
        SimpleClient('listener', self.message_bus, listener=True)

        message = self.client_1.send_message({"data": "Hello"}, ['client_2', 'client_3'])

        # The message should have been delivered to the listener
        self.assertEqual(len(self.message_bus.storage.inboxes[self.message_bus.id]['listener']), 1)
        self.assertEqual(self.message_bus.storage.inboxes[self.message_bus.id]['listener'][0].content, message.content)


if __name__ == '__main__':
    unittest.main()
