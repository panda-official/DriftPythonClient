import os

from drift_client import DriftClient

import logging
import sys

logging.basicConfig(level=logging.DEBUG)


def main():
    # Timeseries example

    # Init
    drift_client = DriftClient("10.0.0.153", os.getenv("DRIFT_PASSWORD"))

    # Download historic data
    topics = drift_client.get_topics()

    # Show list of topics
    print(topics)


if __name__ == "__main__":
    sys.exit(main())
