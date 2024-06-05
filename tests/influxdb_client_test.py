"""InfluxDB Client"""

from datetime import datetime

import pytest
from influxdb_client.client.flux_table import FluxRecord

from drift_client.influxdb_client import InfluxDBClient


@pytest.fixture(name="query_api")
def _make_query_api(mocker):
    client_klass = mocker.patch("drift_client.influxdb_client.Client")
    client = mocker.Mock()
    client.query_api.return_value = mocker.Mock()
    client_klass.return_value = client

    return client.query_api.return_value


@pytest.fixture(name="dt")
def _make_dt() -> datetime:
    return datetime.now()


@pytest.fixture(name="response")
def _make_response(mocker, dt):
    record1 = FluxRecord("", values={"_time": dt, "_value": 1, "_field": "field"})
    record2 = FluxRecord("", values={"_time": dt, "_value": "str", "_field": "field"})

    table = mocker.Mock
    table.records = [record1, record2]
    return [table]


@pytest.fixture(name="response_multi")
def _make_response_multy(mocker, dt):
    record1 = FluxRecord("", values={"_time": dt, "_value": 1, "_field": "field_1"})
    record2 = FluxRecord("", values={"_time": dt, "_value": "str", "_field": "field_2"})

    table = mocker.Mock
    table.records = [record1, record2]
    return [table]


def test__query_data_for_one_field(response, dt, query_api):
    """Should query data and filter it with a field"""
    query_api.query.return_value = response
    influxdb_client = InfluxDBClient(
        "http://localhost:8086", org="panda", secure=False, token="SECRET", timeout=30
    )
    data = influxdb_client.query_data("topic", 1000, 2000, fields="field")

    assert data["field"][0] == (dt.timestamp(), 1)
    assert data["field"][1] == (dt.timestamp(), "str")

    query_api.query.assert_called_with(
        'from(bucket:"data") |> range(start:1000, stop: 2000) |> '
        'filter(fn: (r) => r._measurement == "topic" and ( r._field == "field"))'
    )


def test__query_data_for_some_fields(response_multi, dt, query_api):
    """Should query data and filter it with a few fields"""
    query_api.query.return_value = response_multi

    influxdb_client = InfluxDBClient(
        "http://localhost:8086", org="panda", secure=False, token="SECRET", timeout=30
    )
    data = influxdb_client.query_data(
        "topic", 1000, 2000, fields=["field_1", "field_2"]
    )

    assert data["field_1"][0] == (dt.timestamp(), 1)
    assert data["field_2"][0] == (dt.timestamp(), "str")

    query_api.query.assert_called_with(
        'from(bucket:"data") |> range(start:1000, stop: 2000) |> '
        'filter(fn: (r) => r._measurement == "topic" and ( r._field == "field_1" or '
        'r._field == "field_2"))',
    )


def test__query_data_for_all_fields(response_multi, dt, query_api):
    """Should query data for all fields"""

    query_api.query.return_value = response_multi

    influxdb_client = InfluxDBClient(
        "http://localhost:8086", org="panda", secure=False, token="SECRET", timeout=30
    )
    data = influxdb_client.query_data("topic", 1000, 2000)

    assert data["field_1"][0] == (dt.timestamp(), 1)
    assert data["field_2"][0] == (dt.timestamp(), "str")

    query_api.query.assert_called_with(
        'from(bucket:"data") |> range(start:1000, stop: 2000) |> '
        'filter(fn: (r) => r._measurement == "topic" )',
    )
