import os

from drift_client import DriftClient

import logging
import sys
import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # Init
    drift_client = DriftClient(
        "192.168.1.25", os.getenv("DRIFT_PASSWORD"), timeout=100.0
    )
    metrics = drift_client.get_metrics(
        "energy-distr-1",
        start=datetime.datetime.now() - datetime.timedelta(minutes=15),
        stop=datetime.datetime.now(),
        names=["d1", "d2"],
    )

    print("Loaded %d points", len(metrics))
    for point in metrics:
        print(point)


if __name__ == "__main__":
    sys.exit(main())
