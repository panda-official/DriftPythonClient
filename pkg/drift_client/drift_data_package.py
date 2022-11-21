"""Wrapper around DriftPackage"""
from typing import Optional

from wavelet_buffer import WaveletBuffer  # pylint: disable=no-name-in-module
from drift_protocol.meta import MetaInfo
from drift_protocol.common import DataPayload, DriftPackage, StatusCode
import numpy as np


def check_status(func):
    """Check Package status"""

    def dec(self, **kwargs):
        if self._pkg.status != StatusCode.GOOD:  # pylint: disable=protected-access
            raise ValueError("Bad package")
        return func(self, **kwargs)

    return dec


class DriftDataPackage:  # pylint: disable=no-member
    """Parsed Drift Package with data payload"""

    _blob: bytes
    _pkg: DriftPackage

    def __init__(self, blob: bytes):
        """Parsed Drift Package

        Args:
            blob: Serialized  package from database or stream
        """
        self._blob = blob
        pkg = DriftPackage()
        pkg.ParseFromString(blob)
        self._pkg = pkg

    TS_PRECISION = 1000

    @property
    def blob(self) -> bytes:
        """Serialized DriftPackage, can be passed to file write to save .dp file

        Returns:
            Serialized DriftPackage
        """
        return self._blob

    @property
    def package_id(self) -> int:
        """Package ID

        Returns:
            Package ID (by this all acquired data is synced)
        """
        return self._pkg.id

    @property
    def source_timestamp(self) -> float:
        """Source Timestamp

        Returns:
            Source timestamp (Timestamp when the service
                has received  the input package)
        """
        return self._pkg.source_timestamp.ToMilliseconds() / self.TS_PRECISION

    @property
    def publish_timestamp(self) -> float:
        """Publish Timestamp

        Returns:
            Publish timestamp (Timestamp when the service
                has done its job and sends the output package.)
        """
        return self._pkg.publish_timestamp.ToMilliseconds() / self.TS_PRECISION

    @property
    def status_code(self) -> int:
        """Status Code

        Returns:
            Status of the package. Ok (0) means the package is valid
        """
        return self._pkg.status

    @property
    def meta(self) -> Optional[MetaInfo]:
        """Meta information

        Returns:
            Meta information about the package
        """
        return self._pkg.meta

    @check_status
    def as_raw(self) -> Optional[bytes]:
        """Data payload as raw

        Returns:
            Data payload as raw. None if no payload in the package
        """
        data = None
        for proto_data in self._pkg.data:
            if proto_data.Is(DataPayload.DESCRIPTOR):
                payload = DataPayload()
                proto_data.Unpack(payload)
                data = payload.data

        return data

    @check_status
    def as_buffer(self) -> WaveletBuffer:
        """Data payload as Wavelet Buffer

        Returns:
            Data payload as Wavelet Buffer
        """
        payload = self.as_raw()
        return WaveletBuffer.parse(payload)

    @check_status
    def as_np(self, scale_factor: int = 0) -> np.ndarray:
        """Data payload as NumPy Array

        Args:
            scale_factor: Wavelet composition factor, defaults to 0
        Returns:
            Data payload as NumPy Array
        """
        return self.as_buffer().compose(scale_factor)
