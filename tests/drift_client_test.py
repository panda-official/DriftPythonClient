"""Tests for DriftClient"""
import pytest
from drift_client import DriftClient


@pytest.fixture(name="minio_klass")
def _mock_minio_class(mocker):
    return mocker.patch("drift_client.drift_client.MinIOClient")


@pytest.fixture(name="influxdb_klass")
def _mock_influx_class(mocker):
    return mocker.patch("drift_client.drift_client.InfluxDBClient")


def test__default_initialization(minio_klass, influxdb_klass):
    """should initialize clients with default settings"""
    _ = DriftClient("host_name", "password")

    minio_klass.assert_called_with("http://host_name:9000", "panda", "password", False)
    influxdb_klass.assert_called_with(
        "http://host_name:8086", "panda", "password", False
    )
