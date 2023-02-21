import os

from drift_client import DriftClient

import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # Init
    drift_client = DriftClient("10.66.35.23", os.getenv("DRIFT_PASSWORD"))

    # Download single package
    package = drift_client.get_item("acc-5/1648457411593.dp")

    print(
        package.package_id,
        datetime.fromtimestamp(package.source_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        datetime.fromtimestamp(package.publish_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        package.status_code,
        package.meta,
        package.as_np(),
    )


if __name__ == "__main__":
    sys.exit(main())
