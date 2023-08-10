import httpx

from rustic_ai.messagebus.message import Message


def build_url_callback_method(url: str):
    """Builds a callback method that sends a POST request to the given URL."""

    def callback(message: Message):
        """Sends a POST request to the given URL."""
        with httpx.Client() as client:
            client.post(url, json=message.serialize())

    return callback
