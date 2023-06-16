import os

from drift_client import DriftClient

import logging
import sys

logging.basicConfig(level=logging.DEBUG)


def main():
    # Timeseries example

    # Init
    drift_client = DriftClient("drift-dev2.local", os.getenv("DRIFT_PASSWORD"))

    # Download historic data
    topics = drift_client.get_topics()
    # Show list of topics
    print(topics)
    # Download data for topic
    for pkg in drift_client.walk("acc-6", "2023-06-16T10:00", "2023-06-16T10:10"):
        print(pkg)


if __name__ == "__main__":
    sys.exit(main())
