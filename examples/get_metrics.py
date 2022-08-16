import os

from drift_client import DriftClient

import logging
import sys
import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # Init
    drift_client = DriftClient("drift-test-rig.local", os.getenv("DRIFT_PASSWORD"))
    metrics = drift_client.get_metrics(
        "energy-distr-1",
        start=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
        stop=datetime.datetime.utcnow(),
        names=["d1", "d2"],
    )

    print("Loaded %d points", len(metrics))
    for point in metrics:
        print(point)


if __name__ == "__main__":
    sys.exit(main())
