""" Simple InfluxDB client
"""

from typing import List, Tuple, Any
from datetime import datetime

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
        self.__input_time_fmt = "%Y-%m-%d %H:%M:%S"
        self.__output_time_fmt = "%Y-%m-%dT%H:%M:%SZ"
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
        field: str = "src",
    ) -> List[Tuple[float, str]]:
        """InfluxDB queries for values"""
        # Change time format for request
        start = datetime.strptime(start, self.__input_time_fmt).strftime(
            self.__output_time_fmt
        )
        stop = datetime.strptime(stop, self.__input_time_fmt).strftime(
            self.__output_time_fmt
        )

        query = f'\
            from(bucket:"{self.__bucket}")\
            |> range(start:{start}, stop: {stop})\
            |> filter(fn: (r) => r._measurement == "{measurement}"\
                and r._field =~ /{field}/)\
            '
        response = self.__query_api.query(query)

        data = []
        for table in response:
            for record in table.records:
                data.append(
                    (
                        record.get_time().timestamp(),
                        record.get_value(),
                    )
                )

        return data
