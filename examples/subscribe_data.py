import os

from drift_client import DriftClient

import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)


def main():
    # Init
    drift_client = DriftClient("10.0.0.153", os.getenv("DRIFT_PASSWORD"))

    # for output format of 'wb' or 'raw'
    def package_handler(package):
        print(
            package.package_id,
            datetime.fromtimestamp(package.source_timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            datetime.fromtimestamp(package.publish_timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            package.status_code,
            package.meta,
            package.as_np(),
        )

    # Subscribe live data
    drift_client.subscribe_data("acc-5", package_handler)


if __name__ == "__main__":
    sys.exit(main())
