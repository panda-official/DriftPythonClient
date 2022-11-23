""" Simple MinIO client
"""

from typing import Optional, List

from urllib.parse import urlparse
from minio import Minio
from minio.error import S3Error

from .error import DriftClientError


class MinIOClient:
    """Wrapper around `Minio`"""

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        uri: str,
        access_key: str,
        secret_key: str,
        secure: bool,
    ):
        """Create Client for MinIO access

        :param uri: URI, format: <protocol>://<host>:<port>
        :type uri: str
        :param access_key: MinIO access key
        :type access_key: str
        :param secret_key: MinIO secret key
        :type secret_key: str
        :param secure: encryption enabled
        :type secure: bool
        """
        self.__uri = urlparse(uri)
        self.__client = Minio(
            self.__uri.netloc,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.__bucket = "data"

    def check_package_list(self, package_names: List[str]) -> list:
        """Check if packages exist in Minio"""
        # Not possible with Minio
        return package_names

    def fetch_data(self, path: str) -> Optional[bytes]:
        """Fetch object from Minio

        :param path: path in format `path/to/file`
        :type path: str
        :return: Drift package
        :rtype: dp
        """

        response = None
        data = None

        try:
            response = self.__client.get_object(self.__bucket, path)
            data = response.read()
        except S3Error as err:
            raise DriftClientError(f"Could not read item at {path}") from err
        finally:
            if response:
                response.close()
                response.release_conn()

        return data
