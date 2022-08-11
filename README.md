# Drift Python Client

Python Client to access data of Devices on Drift Platform

## Description

Drift Python Client is a high level library to get current or historical data with minimal knowledge about Drift
infrastructure.

## Installing

```
pip install drift-python-client
```

If you need the latest version from GitHub:

```
pip install git+https://github.com/panda-official/DriftPythonClient.git
```

## Usage Example

```python
import os
from datetime import datetime

from drift_client import DriftClient

drift_client = DriftClient("10.0.0.153", os.getenv("DRIFT_PASSWORD"))
# Download list of history

packages = drift_client.get_topic_data(
    "acc-5",
    datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
    datetime.strptime("2022-01-02 00:00:00", "%Y-%m-%d %H:%M:%S")
)

print(packages)
for path in packages:
    data = drift_client.get_item(path).as_np(scale_factor=2)
    print(data)
```
