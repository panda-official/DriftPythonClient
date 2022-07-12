"""Drift Python Client

Drift Client Module for easy access to Compute Devices on the Drift Platform

"""

import time
import logging
from typing import Dict, List, Callable

from google.protobuf.message import DecodeError

from drift_client.drift_data_package import DriftDataPackage
from drift_client.influxdb_client import InfluxDBClient
from drift_client.minio_client import MinIOClient
from drift_client.mqtt_client import MQTTClient

logger = logging.getLogger("drift-client")


class DriftClient:
    """Drift Python Client Class"""

    # pylint: disable=too-many-arguments

    def __init__(self, host: str, password: str, **kwargs):
        """
        Drift Client for easy access to Compute Devices on the Drift Platform

        Args:
            host: hostname or IP of Compute Device
            password: password to access data
        Keyword Args:
            user (str): A user of the platform. Default: "panda"
            org (str): An organisation name. Default: "panda"
            secure (bool): Use HTTPS protocol to access data: Default: False
            minio_port (int): Minio port. Default: 9000
            influx_port (int): InfluxDB port. Default: 8086,
            mqtt_port (int): MQTT port. Default: 1883
        """

        user = kwargs["user"] if "user" in kwargs else "panda"
        org = kwargs["org"] if "org" in kwargs else "panda"
        secure = kwargs["secure"] if "secure" in kwargs else False
        influx_port = kwargs["influx_port"] if "influx_port" in kwargs else 8086
        minio_port = kwargs["minio_port"] if "minio_port" in kwargs else 9000
        mqtt_port = kwargs["mqtt_port"] if "mqtt_port" in kwargs else 1883

        self.__influx_client = InfluxDBClient(
            f"{('https://' if secure else 'http://')}{host}:{influx_port}",
            org,
            password,
            False,
        )  # TBD!!! --> SSL handling!
        self.__minio_client = MinIOClient(
            f"{('https://' if secure else 'http://')}{host}:{minio_port}",
            user,
            password,
            False,
        )  # TBD!!! --> SSL handling!
        self.__mqtt_client = MQTTClient(
            f"mqtt://{host}:{mqtt_port}",
            client_id=f"drift_client_{int(time.time() * 1000)}",
        )

    def get_topics(self) -> List[str]:
        """Returns list of topics (measurements in InfluxDB)

        Returns:
            List of topics available

        Examples:
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.get_topics() # => ['topic-1', 'topic-2', ...]
        """

        topics = self.__influx_client.query_measurements()
        return topics

    def get_list(self, topics: List[str], timeframe: List[str]) -> Dict[str, List[str]]:
        """Returns list of history data from initialised Device

        Args:
            topics: List of topic names, e.g. `["sensor-1", "sensor-2"]`
            timeframe: List with begin and end of request timeframe,
                Format: `2022-02-07 10:00:00`

        Returns:
            List of item names available
        :rtype: List[str]

        Examples:
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.get_list(["topic-1", "topic-2", "topic-3"],
            >>>         ["2022-02-03 10:00:00", "2022-02-03 10:00:10"])
            >>> # => {"topic-1": ['topic-1/1644750600291.dp',
            >>> #                  'topic-1/1644750601291.dp', ...] ... }
        """
        to_request = self.__influx_client.query_data(topics, timeframe[0], timeframe[1])

        data = {}

        if not to_request:
            return data

        for topic in topics:
            data[topic] = []

        for file in to_request:
            data[file.split("/")[0]].append(file)

        return data

    def get_item(self, path: str) -> DriftDataPackage:
        """Returns requested single historic data from initialised Device
        Args:
            path: path of item in storage
        Raises:
            ValueError: In case of broken WaveletBuffer
        Returns:
            Parsed Drift Package

        Examples:
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.get_item("topic-1/1644750605291.dp")
        """
        blob = self.__minio_client.fetch_data(path)
        return DriftDataPackage(blob)

    def subscribe_data(self, topic: str, handler: Callable[[DriftDataPackage], None]):
        """Subscribes to selected topic from initialised Device

        Args:
            topic: MQTT topic
            handler: Handler - own handler function to be used, e.g.
                `def package_handler(package):`

        Examples:
            >>> def package_handler(package: DriftDataPackage) -> None:
            >>>    print(package.meta)
            >>>
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.subscribe_data("topic-1", package_handler)
        """

        def package_handler(message):
            try:
                output = DriftDataPackage(message.payload)
            except DecodeError as exc:
                raise DecodeError("Payload is no Drift Package") from exc
            handler(output)

        self.__mqtt_client.connect()
        self.__mqtt_client.subscribe(topic, package_handler)

        self.__mqtt_client.loop_forever()

    def publish_data(self, topic: str, payload: str):
        """Publishes payload to selected topic on initialised Device

        topic: MQTT topic
        payload: Stringified data, defaults to None

        # Examples
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.publish_data("topic-2", "hello")
        """
        if not self.__mqtt_client.is_connected():
            self.__mqtt_client.connect()
            self.__mqtt_client.loop_start()

        self.__mqtt_client.publish(topic, payload)
