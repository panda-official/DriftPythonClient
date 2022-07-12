from drift_client import DriftClient

import logging
import sys
import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # Init
    drift_client = DriftClient("10.0.0.153")
    # Download list of history
    packages = drift_client.get_list(
        ["acc-5"],
        [
            (datetime.datetime.now() - datetime.timedelta(minutes=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ],
    )

    # Show length of list
    for topic in packages:
        print(topic, "->", packages[topic])


if __name__ == "__main__":
    sys.exit(main())
