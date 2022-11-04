"""Tests for Package"""
# pylint: disable=no-member
import numpy as np
import pytest
from wavelet_buffer import (  # pylint: disable=no-name-in-module
    WaveletBuffer,
    WaveletType,
    denoise,
)
from drift_protocol.common import DriftPackage, StatusCode, DataPayload
from google.protobuf.any_pb2 import Any  # pylint: disable=no-name-in-module)

from drift_client import DriftDataPackage


@pytest.fixture(name="signal")
def _make_signal() -> np.ndarray:
    return np.array([0, 1, 2, 3, 4, 5, 6], dtype=np.float32)


@pytest.fixture(name="buffer")
def _make_buffer(signal: np.ndarray) -> WaveletBuffer:
    buffer = WaveletBuffer(
        signal_shape=signal.shape,
        signal_number=1,
        decomposition_steps=0,
        wavelet_type=WaveletType.NONE,
    )
    buffer.decompose(signal, denoiser=denoise.Null())
    return buffer


@pytest.fixture(name="good_package")
def _make_good_package(buffer: WaveletBuffer) -> DriftPackage:
    pkg = DriftPackage()
    pkg.id = 1
    pkg.status = StatusCode.GOOD
    pkg.source_timestamp.FromMilliseconds(1000)
    pkg.publish_timestamp.FromMilliseconds(2000)

    payload = DataPayload()
    payload.shape.append(1)
    payload.shape.append(buffer.parameters.signal_shape[0])
    payload.data = buffer.serialize()

    any_msg = Any()
    any_msg.Pack(payload)

    pkg.data.append(any_msg)
    return pkg


def test__package_parsing(good_package, buffer, signal):
    """Should parse a package in a constructor"""
    pkg = DriftDataPackage(good_package.SerializeToString())

    assert pkg.package_id == good_package.id
    assert pkg.status_code == StatusCode.GOOD
    assert pkg.source_timestamp == good_package.source_timestamp.ToMilliseconds() / 1000
    assert (
        pkg.publish_timestamp == good_package.publish_timestamp.ToMilliseconds() / 1000
    )

    assert pkg.as_raw() == buffer.serialize()
    assert pkg.as_buffer() == buffer
    assert list(pkg.as_np()) == list(signal)
    assert pkg.blob() == good_package.SerializeToString()
