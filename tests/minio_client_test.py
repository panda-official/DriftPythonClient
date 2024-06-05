"""Minio Client"""

import pytest

from minio.error import S3Error
from drift_client.minio_client import MinIOClient
from drift_client.error import DriftClientError


@pytest.fixture(name="_minio_client")
def _make_minio_client(mocker):
    """fake client which just raises an S3error"""
    client_klass = mocker.patch("drift_client.minio_client.Minio")
    client = mocker.Mock()
    client.get_object = mocker.Mock(
        side_effect=S3Error(
            code="someErrorCode",
            message="Something Went Wrong",
            resource="data",
            request_id="8BADF00D",
            host_id="DEADBEEF",
            response=None,
        )
    )
    client_klass.return_value = client

    return client_klass


def test__rasise_drift_error(_minio_client):
    """make sure client raises correct error"""

    test_path = "non_existant_data.ext"
    client = MinIOClient("localhost:9000", "user", "password", secure=False)
    with pytest.raises(DriftClientError, match=f"Could not read item at {test_path}"):
        client.fetch_data(test_path)
