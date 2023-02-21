"""Tests for DriftClient"""
from datetime import datetime

import pytest
from reduct import ReductError

from drift_client import DriftClient


@pytest.fixture(name="minio_klass")
def _mock_minio_class(mocker):
    return mocker.patch("drift_client.drift_client.MinIOClient")


@pytest.fixture(name="influxdb_klass")
def _mock_influx_class(mocker):
    return mocker.patch("drift_client.drift_client.InfluxDBClient")


@pytest.fixture(name="reduct_klass")
def _mock_reduct_class(mocker):
    return mocker.patch("drift_client.drift_client.ReductStoreClient")


@pytest.fixture(name="influxdb_client")
def _mock_influx_client(mocker, influxdb_klass):
    client = mocker.Mock()
    influxdb_klass.return_value = client
    return client


@pytest.fixture(name="reduct_client")
def _mock_reduct_client(mocker, reduct_klass):
    client = mocker.Mock()
    reduct_klass.return_value = client
    return client


def test__default_initialization(influxdb_klass, reduct_klass):
    """should initialize clients with default settings"""
    _ = DriftClient("host_name", "password")

    reduct_klass.assert_called_with("http://host_name:8383", "password", None)
    influxdb_klass.assert_called_with(
        "http://host_name:8086", "panda", "password", False
    )


def test__minio_password_required(minio_klass, reduct_klass):
    """should raise error if no password is not provided"""
    with pytest.raises(ValueError):
        _ = DriftClient("host_name", None)


@pytest.mark.usefixtures("minio_klass")
def test__minio_fallback(reduct_klass, minio_klass):
    """should initialize minio client if ReductStore is not available"""
    reduct_klass.side_effect = ReductError(599, "Connection error")

    _ = DriftClient("host_name", "password")
    minio_klass.assert_called_with("http://host_name:9000", "panda", "password", False)


@pytest.mark.usefixtures("reduct_klass")
def test__timestamp_from_influxdb(influxdb_client):
    """should get timestamp and values for records
    from influxdb and make paths in minio"""
    client = DriftClient("host_name", "password")
    influxdb_client.query_data.return_value = {"status": [(10000.0, 0), (10010.0, 512)]}

    data = client.get_list(["topic"], ["2022-01-01 00:00:00", "2022-01-01 00:00:00"])
    assert data == {"topic": ["topic/10000000.dp", "topic/10010000.dp"]}

    influxdb_client.query_data.assert_called_with(
        "topic", "2022-01-01 00:00:00", "2022-01-01 00:00:00", fields="status"
    )


start = datetime.fromisoformat("2022-01-01 00:00:00+01:00")
stop = datetime.fromisoformat("2022-01-01 00:00:00+01:00")


@pytest.mark.parametrize(
    "start_ts, stop_ts",
    [
        (start, stop),
        (start.isoformat(), stop.isoformat()),
        (start.timestamp(), stop.timestamp()),
    ],
)
def test__get_topic_data(influxdb_client, reduct_client, start_ts, stop_ts):
    """should get timestamp and values for records using start and stop timestamps
    from influxdb and make paths in minio"""
    client = DriftClient("host_name", "password")
    influxdb_client.query_data.return_value = {"status": [(10000.0, 0), (10010.0, 512)]}
    expected = [
        "topic/10000000.dp",
        "topic/10010000.dp",
    ]
    reduct_client.check_package_list.return_value = expected

    data = client.get_package_names("topic", start_ts, stop_ts)
    assert data == expected

    influxdb_client.query_data.assert_called_with(
        "topic", 1640991600, 1640991600, fields="status"
    )
    reduct_client.check_package_list.assert_called_with(expected)


@pytest.mark.usefixtures("reduct_klass")
@pytest.mark.parametrize(
    "start_ts, stop_ts",
    [
        (start, stop),
        (start.isoformat(), stop.isoformat()),
        (start.timestamp(), stop.timestamp()),
    ],
)
def test__get_metrics(influxdb_client, start_ts, stop_ts):
    """Should get metrics from InfluxDB and return it like a list of dictioniers"""
    client = DriftClient("host_name", "password")
    influxdb_client.query_data.return_value = {
        "filed_1": [(10000.0, 1), (10010.0, 2)],
        "filed_2": [(10000.0, 3), (10010.0, 4)],
    }

    data = client.get_metrics("topic", start_ts, stop_ts, names=["field_1", "field_2"])
    assert data == [
        {"filed_1": 1, "filed_2": 3, "time": 10000.0},
        {"filed_1": 2, "filed_2": 4, "time": 10010.0},
    ]

    influxdb_client.query_data.assert_called_with(
        "topic",
        1640991600,
        1640991600,
        fields=["field_1", "field_2"],
    )
