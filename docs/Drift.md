# What is PANDA|Drift?

**PANDA|Drift** is a microservice platform to deliver AI applications into the industrial environment which provides the
following features:

### Data Acquisition

The platform has microservices to gather data from different data source.
For example, the data source can be an OPCUA server of an automation system, a vibration sensor or a CV camera.

### Data Processing

AI applications need AI-ready data. **PANDA|Drift** converts all data to unified format, denoises and compresses it.
See our open source library [WaveletBuffer](https://github.com/panda-official/WaveletBuffer) to know how we do this.

### Data Storing

The platform stores a history of input data and results of AI algorithms,
so that they can be used for model training or validation and data visualisation.

### AI Application Server

An AI application can be easily integrated to **PANDA|Drift** infrastructure as a microservice by using MQTT and
[DriftProtocol](https://github.com/panda-official/DriftProtocol)


## Architecture

From high level

![PANDA|Drift Architecture](/docs/img/DrfitStrutcure.drawio.png "")
