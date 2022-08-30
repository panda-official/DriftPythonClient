# What is PANDA|Drift?

_PANDA|Drift_ is a microservice platform to deliver AI applications into the industrial environment, which provides the
following features:

**Data Acquisition**

The platform has microservices to gather data from different data source.
For example, the data source can be an OPCUA server of an automation system, a vibration sensor or a CV camera.

**Data Processing**

AI applications need AI-ready data. _PANDA|Drift_ converts all data to unified format, denoises and compresses it.
See our open-source library [WaveletBuffer][1] to know how we do this.

**Data Storing**

The platform stores a history of input data and results of AI algorithms,
so that they can be used for model training or validation and data visualization.

**AI Application Server**

An AI application can be easily integrated into _PANDA|Drift_ infrastructure as a microservice by using MQTT and
[DriftProtocol][2]

## Architecture

**PANDA|Drift** has a highly grained microservice architecture.
However, it can be presented with few subsystems:

![PANDA|Drift Architecture](/docs/img/DrfitStrutcure.drawio.png "")

Our core technology is the MQTT protocol for real-time communication between microservices.
The Data Accusation layer collects data from data source, denoise and compress it by using [WaveletBuffer][1], then
wraps the data into [DriftProtocol][2] and sends it via MQTT, so that all other parts of the system can use it.

The AI Services process the input data and provide metrics as results. It can be anomaly scores,
coordinates of detected objects etc.

As you may notice, we have two types of data: processed input and metrics. _PANDA|Drift_ keeps a history for both
of them, but it does it differently and for different purposes:

* Metrics are result of work an AI application and this is data that users need. To store it, we use InfluxDB and keep
  data for the long term.
* Input Data are mostly needed for training and model validation. We store it as blobs for the short term and use Minio
  to provide HTTP access to it.

## Integration

To extend systems based on the platform or integrate them into a third-party infrastructure, we
developed [Drift Python Client][3] and made it available as an open-source library.

[1]:https://github.com/panda-official/WaveletBuffer

[2]:https://github.com/panda-official/DriftProtocol

[3]:https://github.com/panda-official/DriftPythonClient
