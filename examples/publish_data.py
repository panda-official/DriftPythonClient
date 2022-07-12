from drift_client import DriftClient

import logging
import sys
import time

logging.basicConfig(level=logging.INFO)


def main():
    # Timeseries example

    # Init
    drift_client = DriftClient("10.0.0.153")

    # Publish data
    i = 0
    while True:
        i = i + 1
        drift_client.publish_data("hello", f"world-{i}")
        time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
