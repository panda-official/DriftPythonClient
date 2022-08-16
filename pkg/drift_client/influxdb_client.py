""" Simple InfluxDB client
"""

from typing import List, Tuple, Any, Union, Dict
from urllib.parse import urlparse

from influxdb_client import InfluxDBClient as Client


class InfluxDBClient:
    """Wrapper around `InfluxDBClient`"""

    def __init__(
        self,
        uri: str,
        org: str,
        token: str,
        secure: bool,
    ):
        """Create Client for InfluxDB access

        :param uri: URI, format: <protocol>://<host>:<port>
        :type uri: str
        :param org: organisation
        :type org: str
        :param token: token
        :type token: str
        :param secure: encryption enabled
        :type secure: bool
        """
        self.__uri = urlparse(uri)
        self.__client = Client(
            url=f"{self.__uri.scheme}://{self.__uri.netloc}",
            org=org,
            token=token,
            verify_ssl=secure,
        )
        self.__query_api = self.__client.query_api()
        self.__bucket = "data"

    def query_measurements(self) -> List[str]:
        """InfluxDB query for measurements

        :return: List of measurements
        :rtype: List[str]
        """
        response = self.__query_api.query(
            f"""\
            import \"influxdata/influxdb/schema\"

            schema.measurements(bucket: \"{self.__bucket}\")
            """
        )

        data = []
        for table in response:
            for record in table.records:
                data.append(record.get_value())

        return data

    def query_data(
        self,
        measurement: str,
        start: str,
        stop: str,
        fields: Union[str, List[str], None] = None,
    ) -> Dict[str, List[Tuple[float, Any, str]]]:
        """InfluxDB queries for values"""
        # Change time format for request
        if isinstance(fields, str):
            fields = [fields]

        filters = ""
        if fields is not None:
            filters = (
                "and ("
                + " or".join([f' r._field == "{field}"' for field in fields])
                + ")"
            )

        query = (
            f'from(bucket:"{self.__bucket}") '
            f"|> range(start:{start}, stop: {stop}) "
            f'|> filter(fn: (r) => r._measurement == "{measurement}" {filters})'
        )

        response = self.__query_api.query(query)

        data = {}
        for table in response:
            for record in table.records:
                field = record.get_field()
                if field not in data:
                    data[field] = []
                data[field].append((record.get_time().timestamp(), record.get_value()))

        return data
