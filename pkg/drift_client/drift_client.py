"""Drift Python Client

Drift Client Module for easy access to Compute Devices on the Drift Plattform

"""

import time
import logging
from typing import Dict, List, Callable, Optional

import numpy as np

from drift_protocol.common import DataPayload, DriftPackage, StatusCode
from drift_protocol.meta import MetaInfo
from google.protobuf.message import DecodeError
from wavelet_buffer import WaveletBuffer  # pylint: disable=no-name-in-module

from drift_client.influxdb_client import InfluxDBClient
from drift_client.minio_client import MinIOClient
from drift_client.mqtt_client import MQTTClient

logger = logging.getLogger("drift-client")


def check_status(func):
    """Check Package status"""

    def dec(self):
        if self._pkg.status != StatusCode.GOOD:  # pylint: disable=protected-access
            raise ValueError("Bad package")
        return func(self)

    return dec


class Package:  # pylint: disable=no-member
    """Parsed Drift Package Class"""

    _pkg: DriftPackage

    def __init__(self, blob: bytes):
        """Parsed Drift Package

        :param blob: Blob from database or stream
        :type blob: bytes
        """
        pkg = DriftPackage()
        pkg.ParseFromString(blob)
        self._pkg = pkg

    TS_PRECISION = 1000

    @property
    def package_id(self) -> int:
        """Package ID

        :return: Package ID (by this all acquired data is synced)
        :rtype: int
        """
        return self._pkg.id

    @property
    def source_timestamp(self) -> float:
        """Source Timestamp

        :return: Source timestamp (Timestamp when the service
            has received  the input package)
        :rtype: float
        """
        return self._pkg.source_timestamp.ToMilliseconds() / self.TS_PRECISION

    @property
    def publish_timestamp(self) -> float:
        """Publish Timestamp

        :return: Publish timestamp (Timestamp when the service
            has done its job and sends the output package.)
        :rtype: float
        """
        return self._pkg.publish_timestamp.ToMilliseconds() / self.TS_PRECISION

    @property
    def status_code(self) -> int:
        """Status Code

        :return: Status of the package. Ok (0) means the package is valid
        :rtype: int
        """
        return self._pkg.status

    @property
    def meta(self) -> Optional[MetaInfo]:
        """_summary_

        :return: Meta information about the package
        :rtype: Optional[MetaInfo]
        """
        return self._pkg.meta

    @check_status
    def as_raw(self) -> Optional[bytes]:
        """Data payload as raw

        :return: Data payload as raw
        :rtype: Optional[bytes]
        """
        data = None
        for proto_data in self._pkg.data:
            if proto_data.Is(DataPayload.DESCRIPTOR):
                payload = DataPayload()
                proto_data.Unpack(payload)
                data = payload.data

        return data

    @check_status
    def as_buffer(self) -> WaveletBuffer:
        """Data payload as Wavelet Buffer

        :return: Data payload as Wavelet Buffer
        :rtype: WaveletBuffer
        """
        return WaveletBuffer.parse(self.as_raw())

    @check_status
    def as_np(self, scale_factor: int = 0) -> np.ndarray:
        """Data payload as NumPy Array

        :param scale_factor: Wavelet composition factor, defaults to 0
        :type scale_factor: int, optional
        :return: Data payload as NumPy Array
        :rtype: np.ndarray
        """
        return self.as_buffer().compose(scale_factor)


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
            timeframe: List with begin and end of request timeframe, Format: `2022-02-07 10:00:00`

        Returns:
            List of item names available
        :rtype: List[str]

        Examples:
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.get_list(["topic-1", "topic-2", "topic-3"], ["2022-02-03 10:00:00", "2022-02-03 10:00:10"])
            >>>     # => {"topic-1": ['topic-1/1644750600291.dp', 'topic-1/1644750601291.dp', ...] ... }
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

    def get_item(self, item: str) -> Package:
        """Returns requested single historic data from initialised Device
        ~~~~~~~~~~~~~~~STOP_POINT
        Args:
            item:
        :param item: Item name
        :type item: str
        :raises ValueError: In case of broken WaveletBuffer
        :return: Parsed Drift Package
        :rtype: Package

        .. highlight:: python
        .. code-block:: python

            # Example
            client.get_item("topic-1/1644750605291.dp")
        """
        blob = self.__minio_client.fetch_data(item)
        return Package(blob)

    def subscribe_data(self, topic: str, handler: Callable):
        """Subscribes to selected topic from initialised Device

        :param topic: MQTT topic
        :type topic: str
        :param handler: Handler - own handler function to be used, e.g.
            `def package_handler(package):`
        :type handler: Callable

        .. highlight:: python
        .. code-block:: python

            # Example
            def package_handler(*package):
                print(package.meta)

            client.subscribe_data("topic-1", package_handler)
        """

        def package_handler(message):
            try:
                output = Package(message.payload)
            except DecodeError as exc:
                raise DecodeError("Payload is no Drift Package") from exc
            handler(output)

        self.__mqtt_client.connect()
        self.__mqtt_client.subscribe(topic, package_handler)

        self.__mqtt_client.loop_forever()

    def publish_data(self, topic: str, payload: str = None):
        """Publishs payload to selected topic on initialised Device

        :param topic: MQTT topic
        :type topic: str
        :param payload: Stringified data, defaults to None
        :type payload: str, optional

        # Example
        client.publish_data("topic-2", "hello")
        """
        if not self.__mqtt_client.is_connected():
            self.__mqtt_client.connect()
            self.__mqtt_client.loop_start()

        self.__mqtt_client.publish(topic, payload)
