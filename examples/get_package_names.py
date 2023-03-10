import os
from datetime import timezone

from drift_client import DriftClient

import logging
import sys
import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # Init
    drift_client = DriftClient("tesa-1d2.local", os.getenv("DRIFT_PASSWORD"))
    # Download list of history
    packages = drift_client.get_package_names(
        "camera",
        start=datetime.datetime.now() - datetime.timedelta(minutes=1),
        stop=datetime.datetime.now(),
    )

    # Show length of list
    print(packages)


if __name__ == "__main__":
    sys.exit(main())
