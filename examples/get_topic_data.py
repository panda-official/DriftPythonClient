import os

from drift_client import DriftClient

import logging
import sys
import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # Init
    drift_client = DriftClient("drift-test-rig.local", os.getenv("DRIFT_PASSWORD"))
    # Download list of history
    packages = drift_client.get_topic_data(["acc-1", "acc-2"],
                                           start=datetime.datetime.utcnow() -
                                                 datetime.timedelta(minutes=1),
                                           stop=datetime.datetime.utcnow())

    # Show length of list
    for topic in packages:
        print(topic, "->", packages[topic])


if __name__ == "__main__":
    sys.exit(main())
