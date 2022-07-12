""" Simple InfluxDB client
"""

from typing import List
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
        response = None
        data = []
        response = self.__query_api.query(
            f"""\
            import \"influxdata/influxdb/schema\"

            schema.measurements(bucket: \"{self.__bucket}\")
            """
        )

        for table in response:
            for record in table.records:
                data.append(record.get_value())

        return data

    def query_data(
        self,
        measurements: List[str],
        start: str,
        stop: str,
        field: str = "src",
    ) -> List[str]:
        """InfluxDB query for values

        :param measurements: List of InfluxDB measurement names
        :type measurements: List[str]
        :param start: Range start in format %Y-%m-%d %H:%M:%S
        :type start: str
        :param stop: Range stop in format %Y-%m-%d %H:%M:%S
        :type stop: str
        :param field: InfluxDB field name, defaults to "_src"
        :type field: str, optional
        :return: List of values according to measurement and field filter
        :rtype: List[str]
        """
        # Change time format for request
        start = datetime.strptime(start, self.__input_time_fmt).strftime(
            self.__output_time_fmt
        )
        stop = datetime.strptime(stop, self.__input_time_fmt).strftime(
            self.__output_time_fmt
        )

        # For only matching exact topic names from measurements list
        # pylint: disable=consider-using-f-string
        measurements_regex = "(?:{})".format(
            "|".join(["^{}\\b".format(x) for x in measurements])
        )

        response = self.__query_api.query(
            f'\
            from(bucket:"{self.__bucket}")\
            |> range(start:{start}, stop: {stop})\
            |> filter(fn: (r) => r._measurement =~ /{measurements_regex}/\
                and r._field =~ /{field}/)\
            |> keep(columns: ["_value"])\
            '
        )

        data = []
        for table in response:
            for record in table.records:
                data.append(record.get_value())

        return data
