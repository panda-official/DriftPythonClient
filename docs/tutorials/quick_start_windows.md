# Quick Start for Windows users

This tutorial will help you to install Drift python client on Windows and run a simple example.

# Installing Python

First of all, you need to install Python 3.8, 3.9 or 3.10. You can download it
from [python.org](https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe).
Run the installer. After installation, you can check the version of Python by running the following command in the
terminal:

```bash
py --version
```

Then update the `pip` package manager:

```bash
py -m pip install --upgrade pip
```

# Installing DriftPythonClient

The DriftPythonClient is available on [PyPI](https://pypi.org/project/drift-python-client/). You can install it by
running the following command:

```bash
py -m pip install drift-python-client
```

It has prebuilt binaries for Windows, so you don't need to install any additional dependencies except Visual C++
Redistributable for Visual Studio. You can download it
from [here](https://www.microsoft.com/en-us/download/confirmation.aspx?id=48145).

# Quick Check

## Get metrics and raw data from Drift device

write a script `quick_check.py`:

```python

import os
from datetime import datetime, timedelta

from drift_client import DriftClient

drift_client = DriftClient(os.getenv("DRIFT_DEVICE"), os.getenv("DRIFT_PASSWORD"))

print("Available topics: ", drift_client.get_topics())

start_time = datetime.utcnow() - timedelta(days=1)
stop_time = datetime.utcnow()
metrics = drift_client.get_metrics(
    "energy-acc-1",
    start=start_time,
    stop=stop_time
)

print("Loaded %d points", len(metrics))
for point in metrics:
    print(point)

last_acc_5 = drift_client.get_package_names(
    "acc-5",
    start_time,
    stop_time)[-1]

print("Last acc-5 package: ", last_acc_5)
print("Scaled x4 times signal: ", drift_client.get_item(last_acc_5).as_np(scale_factor=2))
```

run script with environment variables

```
set DRIFT_DEVICE=<your device ip>
set DRIFT_PASSWORD=<your device password>
python quick_check.py
```