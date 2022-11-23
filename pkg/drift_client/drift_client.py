"""Drift Python Client

Drift Client Module for easy access to Compute Devices on the Drift Platform

"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Callable, Union, Any, Optional

import deprecation
from google.protobuf.message import DecodeError

from drift_client.drift_data_package import DriftDataPackage
from drift_client.influxdb_client import InfluxDBClient
from drift_client.minio_client import MinIOClient
from drift_client.mqtt_client import MQTTClient
from drift_client.reduct_client import ReductStorageClient

logger = logging.getLogger("drift-client")
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _convert_type(timestamp: Union[float, datetime, str]) -> str:
    if isinstance(timestamp, str):
        return datetime.fromisoformat(timestamp).strftime(TIME_FORMAT)
    if isinstance(timestamp, float):
        return datetime.fromtimestamp(timestamp).strftime(TIME_FORMAT)
    if isinstance(timestamp, datetime):
        return timestamp.strftime(TIME_FORMAT)
    raise TypeError("Timestamp must be str, float or datetime")


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
            reduct_port (int): Reduct port. Default: 8383
            influx_port (int): InfluxDB port. Default: 8086,
            mqtt_port (int): MQTT port. Default: 1883
        """

        user = kwargs["user"] if "user" in kwargs else "panda"
        org = kwargs["org"] if "org" in kwargs else "panda"
        secure = kwargs["secure"] if "secure" in kwargs else False
        influx_port = kwargs["influx_port"] if "influx_port" in kwargs else 8086
        minio_port = kwargs["minio_port"] if "minio_port" in kwargs else 9000
        reduct_storage_port = (
            kwargs["reduct_storage_port"] if "reduct_storage_port" in kwargs else 8383
        )
        mqtt_port = kwargs["mqtt_port"] if "mqtt_port" in kwargs else 1883

        self._influx_client = InfluxDBClient(
            f"{('https://' if secure else 'http://')}{host}:{influx_port}",
            org,
            password,
            False,
        )  # TBD!!! --> SSL handling!

        try:
            self._blob_storage = ReductStorageClient(
                f"{('https://' if secure else 'http://')}{host}:{reduct_storage_port}",
                password,
            )
        except Exception:  # pylint: disable=broad-except
            # Minio as fallback if reduct storage is not available
            self._blob_storage = MinIOClient(
                f"{('https://' if secure else 'http://')}{host}:{minio_port}",
                user,
                password,
                False,
            )  # TBD!!! --> SSL handling!
        self._mqtt_client = MQTTClient(
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

        topics = self._influx_client.query_measurements()
        return topics

    @deprecation.deprecated(
        deprecated_in="0.2.0",
        removed_in="1.0.0",
        details="use drift_client.get_topic_data method instead",
    )
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
        data = {}
        for topic in topics:
            influxdb_values = self._influx_client.query_data(
                topic, timeframe[0], timeframe[1], fields="status"
            )

            if not influxdb_values:
                break

            data[topic] = []
            for timestamp, _ in influxdb_values["status"]:
                data[topic].append(f"{topic}/{int(timestamp * 1000)}.dp")

        return data

    def get_package_names(
        self,
        topic: str,
        start: Union[float, datetime, str],
        stop: Union[float, datetime, str],
    ) -> List[str]:
        """Returns list of history data from initialised Device

        Args:
            topic: Topic name
            start: Begin of request timeframe,
                Format: ISO string, datetime or float timestamp
            stop: End of request timeframe,
                Format: ISO string, datetime or float timestamp

        Returns:
            List with item names available

        Examples:
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.get_package_names("topic-1",
            >>>         "2022-02-03 10:00:00", "2022-02-03 10:00:10")
            >>> # => ['topic-1/1644750600291.dp',
            >>> #                  'topic-1/1644750601291.dp', ...]
        """
        start = _convert_type(start)
        stop = _convert_type(stop)

        package_list = []
        influxdb_values = self._influx_client.query_data(
            topic, start, stop, fields="status"
        )

        if influxdb_values:
            for timestamp, _ in influxdb_values["status"]:
                package_list.append(f"{topic}/{int(timestamp * 1000)}.dp")

        # Check if package_list is available (works only for Reduct Storage)
        return self._blob_storage.check_package_list(package_list)

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
        blob = self._blob_storage.fetch_data(path)
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

        self._mqtt_client.connect()
        self._mqtt_client.subscribe(topic, package_handler)

        self._mqtt_client.loop_forever()

    def publish_data(self, topic: str, payload: bytes):
        """Publishes payload to selected topic on initialised Device
        Args:
            topic: MQTT topic
            payload: Stringified data, defaults to None

        Examples
            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.publish_data("topic-2", b"hello")
        """
        if not self._mqtt_client.is_connected():
            self._mqtt_client.connect()
            self._mqtt_client.loop_start()

        self._mqtt_client.publish(topic, payload)

    def get_metrics(
        self,
        topic: str,
        start: Union[float, datetime, str],
        stop: Union[float, datetime, str],
        names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Reads history metrics from timeseries database

        Args:
            topic: MQTT topic
            start: Begin of request timeframe,
                Format: ISO string, datetime or float timestamp
            stop: End of request timeframe,
                Format: ISO string, datetime or float timestamp
            names: Name of metrics, if None get all metrics for the topic

        Examples

            >>> client = DriftClient("127.0.0.1", "PASSWORD")
            >>> client.get_metrics("topic", "2022-02-03 10:00:00",
            >>>    "2022-02-03 10:00:10", names=["status", "field"])
            >>> #=> [{"status": 0, "field": 0.1231}, ....]
        """

        start = _convert_type(start)
        stop = _convert_type(stop)

        aligned_data = {}
        influxdb_values = self._influx_client.query_data(
            topic, start, stop, fields=names
        )

        for field, values in influxdb_values.items():
            for dt, value in values:
                if dt not in aligned_data:
                    aligned_data[dt] = {}

                aligned_data[dt][field] = value

        data = []
        for dt, fields in aligned_data.items():
            fields["time"] = dt
            data.append(fields)

        return data
