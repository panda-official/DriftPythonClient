"""Tests for DriftClient"""
import pytest
from datetime import datetime
from drift_client import DriftClient

@pytest.fixture(name="minio_klass")
def _mock_minio_class(mocker):
    return mocker.patch("drift_client.drift_client.MinIOClient")


@pytest.fixture(name="influxdb_klass")
def _mock_influx_class(mocker):
    return mocker.patch("drift_client.drift_client.InfluxDBClient")


@pytest.fixture(name="influxdb_client")
def _mock_influx_client(mocker, influxdb_klass):
    client = mocker.Mock()
    influxdb_klass.return_value = client
    return client


def test__default_initialization(minio_klass, influxdb_klass):
    """should initialize clients with default settings"""
    _ = DriftClient("host_name", "password")

    minio_klass.assert_called_with("http://host_name:9000", "panda", "password", False)
    influxdb_klass.assert_called_with(
        "http://host_name:8086", "panda", "password", False
    )


@pytest.mark.usefixtures("minio_klass")
def test__timestamp_from_influxdb(influxdb_client):
    """should get timestamp and values for records
    from influxdb and make paths in minio"""
    client = DriftClient("host_name", "password")
    influxdb_client.query_data.return_value = [(10000.0, 0), (10010.0, 512)]

    data = client.get_list(["topic"], ["2022-01-01 00:00:00", "2022-01-01 00:00:00"])
    assert data == {"topic": ["topic/10000000.dp", "topic/10010000.dp"]}

    influxdb_client.query_data.assert_called_with(
        "topic", "2022-01-01 00:00:00", "2022-01-01 00:00:00", field="status"
    )

@pytest.mark.usefixtures("minio_klass")
def test__get_topic_data(influxdb_client):
    """should get timestamp and values for records using start and stop timestamps
    from influxdb and make paths in minio"""
    client = DriftClient("host_name", "password")
    influxdb_client.query_data.return_value = [(10000.0, 0), (10010.0, 512)]

    start = datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    stop = datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    data = client.get_topic_data(["topic"], start, stop)
    assert data == {"topic": ["topic/10000000.dp", "topic/10010000.dp"]}

    influxdb_client.query_data.assert_called_with(
        "topic", "2022-01-01 00:00:00", "2022-01-01 00:00:00", field="status"
    )

    data = client.get_topic_data(["topic"], start.isoformat(), stop.isoformat())
    assert data == {"topic": ["topic/10000000.dp", "topic/10010000.dp"]}

    influxdb_client.query_data.assert_called_with(
        "topic", "2022-01-01 00:00:00", "2022-01-01 00:00:00", field="status"
    )

    data = client.get_topic_data(["topic"], start.timestamp(), stop.timestamp())
    assert data == {"topic": ["topic/10000000.dp", "topic/10010000.dp"]}

    influxdb_client.query_data.assert_called_with(
        "topic", "2022-01-01 00:00:00", "2022-01-01 00:00:00", field="status"
    )
