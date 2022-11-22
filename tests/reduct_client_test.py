"""Reduct Storage Client"""

import pytest
from reduct import ServerInfo, BucketSettings, Bucket, EntryInfo
from reduct.bucket import Record
from reduct.client import Defaults, Client

from drift_client.reduct_client import ReductStorageClient


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
        _ = ReductStorageClient("http://localhost:8383", "password")


@pytest.mark.usefixtures("reduct_client")
def test__check_packages_names_available(bucket):
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

    client = ReductStorageClient("http://localhost:8383", "password")
    assert client.check_package_list(
        ["topic/1.dp", "topic/2.dp", "topic/3.dp", "topic/4.dp"]
    ) == ["topic/2.dp", "topic/3.dp"]
    assert client.check_package_list(["unknown/3.dp", "unknown/4.dp"]) == []


@pytest.mark.usefixtures("reduct_client")
def test__fetch_package(mocker, bucket):
    """should fetch package from reduct storage"""

    def make_record(timestamp: int, data: bytes) -> Record:
        async def read_all():
            return data

        async def read(_n: int):
            yield data

        return Record(
            timestamp=timestamp, size=len(data), last=True, read_all=read_all, read=read
        )

    ctx = mocker.MagicMock()
    ctx.__aenter__.return_value = make_record(1000, b"test")
    ctx.__aexit__.return_value = mocker.Mock()
    bucket.read.return_value = ctx

    client = ReductStorageClient("http://localhost:8383", "password")
    assert client.fetch_data("topic/1.dp") == b"test"
