"""Tests for Package"""
from typing import Dict

# pylint: disable=no-member
import numpy as np
import pytest
from google.protobuf.any_pb2 import Any  # pylint: disable=no-name-in-module)

from drift_bytes import Variant, OutputBuffer
from drift_protocol.meta import TypedDataInfo, MetaInfo
from drift_protocol.common import DriftPackage, StatusCode, DataPayload
from drift_client import DriftDataPackage
from wavelet_buffer import (  # pylint: disable=no-name-in-module
    WaveletBuffer,
    WaveletType,
    denoise,
)


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
    payload.data = buffer.serialize()

    any_msg = Any()
    any_msg.Pack(payload)

    pkg.data.append(any_msg)

    label = DriftPackage.Label()
    label.key = "key"
    label.value = "value"

    pkg.labels.append(label)

    return pkg


@pytest.fixture(name="typed_data")
def _make_typed_data() -> Dict[str, Variant.SUPPORTED_TYPES]:
    return {"bool": True, "int": 1, "float": 1.0, "string": "string", "none": None}


@pytest.fixture(name="typed_data_package")
def _make_typed_data_package(
    typed_data: Dict[str, Variant.SUPPORTED_TYPES]
) -> DriftPackage:
    pkg = DriftPackage()
    pkg.id = 1
    pkg.status = StatusCode.GOOD
    pkg.source_timestamp.FromMilliseconds(1000)
    pkg.publish_timestamp.FromMilliseconds(2000)

    buffer = OutputBuffer()
    items = TypedDataInfo()
    for key, value in typed_data.items():
        item = TypedDataInfo.Item()
        item.name = key
        if value is None:
            item.status = StatusCode.BAD
            buffer.push(Variant(False))
        else:
            item.status = StatusCode.GOOD
            buffer.push(Variant(value))
        items.items.append(item)

    pkg.meta.type = MetaInfo.TYPED_DATA
    pkg.meta.typed_data_info.CopyFrom(items)

    payload = DataPayload()
    payload.data = buffer.bytes()

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
    assert pkg.blob == good_package.SerializeToString()


def test__scale_factor(good_package, signal):
    """Should return scaled data"""
    pkg = DriftDataPackage(good_package.SerializeToString())
    assert len(pkg.as_np(scale_factor=1)) == int(len(signal) / 2)


def test__labels(good_package):
    """Should provide access to labels"""
    pkg = DriftDataPackage(good_package.SerializeToString())
    assert pkg.labels == {"key": "value"}


def test__typed_data(typed_data_package, typed_data):
    """Should provide access to typed data"""
    pkg = DriftDataPackage(typed_data_package.SerializeToString())
    assert pkg.as_typed_data() == typed_data
