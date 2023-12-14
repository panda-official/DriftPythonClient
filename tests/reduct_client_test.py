"""Reduct Storage Client"""
from typing import Optional, List, Any

import pytest
from reduct import ServerInfo, BucketSettings, Bucket, EntryInfo, ReductError
from reduct.bucket import Record
from reduct.client import Defaults, Client

from drift_client.error import DriftClientError
from drift_client.reduct_client import ReductStoreClient


class AsyncIter:  # pylint: disable=too-few-public-methods
    """Helper class for efficient mocking"""

    def __init__(self, items: Optional[List[Any]] = None):
        self.items = items if items else []


@pytest.fixture(name="bucket")
def _make_bucket(mocker) -> Bucket:
    bucket = mocker.Mock(spec=Bucket)
    bucket.name = "data"

    return bucket


@pytest.fixture(name="reduct_client")
def _make_reduct_client(mocker, bucket):
    client_klass = mocker.patch("drift_client.reduct_client.Client")
    client = mocker.Mock(spec=Client)
    client.info.return_value = ServerInfo(
        version="1.0.0",
        bucket_count=0,
        usage=0,
        uptime=0,
        oldest_record=0,
        latest_record=0,
        defaults=Defaults(bucket=BucketSettings()),
    )

    client.get_bucket.return_value = bucket
    client_klass.return_value = client
    return client


def test__check_server_available():
    """should check if server is available"""
    with pytest.raises(Exception):
        _ = ReductStoreClient("http://localhost:8383", "password")


@pytest.fixture(name="drift_client")
def _make_drift_client(reduct_client):
    _ = reduct_client
    return ReductStoreClient("http://localhost:8383", "password")


def test__check_packages_names_available(bucket, drift_client):
    """should check if server is available"""
    bucket.get_entry_list.return_value = [
        EntryInfo(
            name="topic",
            size=100,
            block_count=1,
            record_count=1,
            oldest_record=2000,
            latest_record=3000,
        )
    ]

    assert drift_client.check_package_list(
        ["topic/1.dp", "topic/2.dp", "topic/3.dp", "topic/4.dp"]
    ) == ["topic/2.dp", "topic/3.dp"]
    assert drift_client.check_package_list(["unknown/3.dp", "unknown/4.dp"]) == []


def test__fetch_package(mocker, bucket, drift_client):
    """should fetch package from reduct storage"""

    def make_record(timestamp: int, data: bytes) -> Record:
        async def read_all():
            return data

        async def read(_n: int):
            yield data

        return Record(
            timestamp=timestamp,
            size=len(data),
            last=True,
            read_all=read_all,
            read=read,
            content_type="",
            labels={},
        )

    ctx = mocker.MagicMock()
    ctx.__aenter__.return_value = make_record(1000, b"test")
    ctx.__aexit__.return_value = mocker.Mock()
    bucket.read.return_value = ctx

    assert drift_client.fetch_data("topic/1.dp") == b"test"


class _Rec:  # pylint: disable=too-few-public-methods
    def __init__(self, data):
        self.data = data

    async def read_all(self):
        """read all data"""
        return self.data


def test__walk_records(bucket, drift_client):
    """should walk records"""

    items = [b"1", b"2", b"3", b"4", b"5"]

    async def _iter():
        for item in items:
            yield _Rec(item)

    bucket.query.return_value = _iter()

    assert list(drift_client.walk("topic", 0, 1)) == items

    bucket.query.assert_called_with("topic", 0, 1000_000, ttl=60)


def test___walk_with_error(bucket, drift_client):
    """should raise error if failed to walk records"""

    async def _iter():
        yield _Rec(b"1")
        raise ReductError(400, "test")

    bucket.query.return_value = _iter()
    with pytest.raises(DriftClientError):
        list(drift_client.walk("topic", 0, 1))


def test___walk_with_ttl(bucket, drift_client):
    """should walk records with ttl"""

    async def _iter():
        yield _Rec(b"1")

    bucket.query.return_value = _iter()
    list(drift_client.walk("topic", 0, 1, ttl=10))
    bucket.query.assert_called_with("topic", 0, 1000_000, ttl=10)
