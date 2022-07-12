""" Setup script
"""
import os
from pathlib import Path

from setuptools import setup, find_packages

PACKAGE_NAME = "drift-python-client"
MAJOR_VERSION = 0
MINOR_VERSION = 1
PATCH_VERSION = 1
VERSION_SUFFIX = os.getenv("VERSION_SUFFIX")

HERE = Path(__file__).parent.resolve()


def update_package_version(path: Path, version: str):
    """Overwrite/create __init__.py file and fill __version__"""
    with open(path / "VERSION", "w") as version_file:
        version_file.write(f"{version}\n")


def build_version():
    """Build dynamic version and update version in package"""
    version = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
    if VERSION_SUFFIX:
        version += f".{VERSION_SUFFIX}"

    update_package_version(HERE / "pkg" / "drift_client", version=version)

    return version


def get_long_description(base_path: Path):
    """Get long package description"""
    return (base_path / "README.md").read_text(encoding="utf-8")


setup(
    name=PACKAGE_NAME,
    version=build_version(),
    description="Drift Python Client",
    long_description=get_long_description(HERE),
    long_description_content_type="text/markdown",
    url="https://github.com/panda-official/DriftPythonClient",
    author="PANDA, GmbH",
    author_email="info@panda.technology",
    package_dir={"": "pkg"},
    package_data={"": ["VERSION"]},
    packages=find_packages(where="pkg"),
    python_requires=">=3.8",
    install_requires=[
        "influxdb-client==1.30.0",
        "minio==7.1.10",
        "drift-protocol~=0.1.0",
        "wavelet-buffer~=0.1.0",
        "paho-mqtt==1.6.1",
        "numpy==1.23.1",
    ],
    extras_require={
        "test": ["pytest==7.1.2", "pytest-mock==3.8.2"],
        "lint": ["pylint==2.14.4", "pylint-protobuf==0.20.2"],
        "format": ["black==22.6.0"],
        "docs": [
            "mkdocs~=1.3",
            "mkdocs-material~=8.3",
            "plantuml-markdown~=3.5",
            "mkdocs-same-dir~=0.1",
            "mkdocstrings[python]~=0.19",
        ],
    },
)
