""" Simple MQTT client
"""

import logging
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

logger = logging.getLogger("drift-mqtt")


@dataclass
class Subscription:
    """Subscription config"""

    topic: str
    quality_service: int
    handler: Callable


class MQTTClient:
    """Wrapper around `paho.mqtt.Client`
    * correctly handles subscription after reconnect
    * supports connection strings (i.e. protocol://domain:port)
    * supports routing on different message handlers
    """

    def __init__(self, uri: str, client_id: str = "drift-mqtt-client"):
        """Init
        :param uri - <protocol>://<host>:<port>
        :param client_id - must be unique! if not - will cause disconnects
        """
        self._uri = urlparse(uri)
        self._transport = "websockets" if self._uri.scheme == "ws" else "tcp"
        # TODO: check if we need v311 or v5 # pylint: disable=fixme
        self._client = mqtt.Client(client_id=client_id, transport=self._transport)
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect
        self._client.on_subscribe = self.on_subscribe
        self._client.on_message = self.on_message
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)
        self._client.enable_logger()
        self._subscriptions = []

    def on_message(self, _client, _userdata, message: mqtt.MQTTMessage):
        """Message read callback"""
        for sub in self._subscriptions:
            if message.topic.startswith(sub.topic):
                try:
                    sub.handler(message)
                except Exception:  # pylint: disable=broad-except
                    logger.exception("Error in a message handler")

    def __getattr__(self, item):
        """Forward unknown methods to MQTT client"""
        return getattr(self._client, item)

    def connect(self):
        """Connect to mqtt, blocking call, will wait until response.
        It is safe to call subscribe after this.
        """
        self._client.connect(host=self._uri.hostname, port=self._uri.port)
        while not self._client.is_connected():
            self._client.loop()

    def on_connect(self, _client, _userdata, _flags, return_code, _properties=None):
        """Callback on mqtt connected"""
        if return_code == mqtt.MQTT_ERR_SUCCESS:
            logger.info("Connected to MQTT")
            self._subscribe()
        else:
            logger.error(
                "Connection to MQTT refused, code: %d, %s",
                return_code,
                mqtt.error_string(return_code),
            )

    @staticmethod
    def on_disconnect(_client, _userdata, return_code):
        """Callback on mqtt disconnected"""
        # this is a bug in paho, return_code 1 is a general error
        # (connection lost in this case)
        if return_code == mqtt.MQTT_ERR_NOMEM:
            return_code = mqtt.MQTT_ERR_CONN_LOST

        if return_code == mqtt.MQTT_ERR_SUCCESS:
            logger.info("Disconnected from MQTT, as requested")
        else:
            logger.info(
                "Disconnected from MQTT (%s), reconnecting",
                mqtt.error_string(return_code),
            )

    @staticmethod
    def on_subscribe(_client, _userdata, _mid, _granted_qos, _properties=None):
        """Subscribe callback, just log for now"""
        logger.info("Subscribed")

    def _subscribe(self):
        """Subscribe all pending subscriptions"""
        subs = [(sub.topic, sub.quality_service) for sub in self._subscriptions]
        if subs:
            self._client.subscribe(subs)

    def subscribe(self, topic, handler: Callable, quality_service=0):
        """Subscription proxy to delay subscription until we connect to broker"""
        self._subscriptions.append(
            Subscription(topic=topic, quality_service=quality_service, handler=handler)
        )
        if self._client.is_connected():
            self._subscribe()
