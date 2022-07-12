# Drift Python Client

Python Client to access data of Devices on Drift Platform

## Description

Drift Python Client is a high level library to get current or historical data with minimal knowledge about Drift
infrastructure.

## Installing

```
pip install https://github.com/panda-official/DriftPythonClient.git
```

## Usage Example

```python
import os

from drift_client import DriftClient

drift_client = DriftClient("10.0.0.153", os.getenv("DRIFT_PASSWORD"))
# Download list of history
packages = drift_client.get_list(
    ["acc-5"],
    ["2022-01-01 00:00:00", "2022-01-02 00:00:00"],
)

for topic in packages:
    print(topic, "->", packages[topic])
    for path in packages[topic]:
        data = drift_client.get_item(path).as_np(scale_factor=2)
        print(data)
```
