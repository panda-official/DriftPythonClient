# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 0.2.0 - 2022-08-16

### Added:

- DRIFT-478: `Client.get_metrics` to get metrics from InfluxDB, [PR-10](https://github.com/panda-official/DriftPythonClient/pull/10)
- DRIFT-510: Make package paths by using time from InfluxDB, [PR-2](https://github.com/panda-official/DriftPythonClient/pull/2)
- DRIFT-516: `Client.get_topic_data` to get paths in Minio, [PR-5](https://github.com/panda-official/DriftPythonClient/pull/5)

### Deprecated:

- DRIFT-516: `Client.get_list`. Remove in 1.0.0, [PR-5](https://github.com/panda-official/DriftPythonClient/pull/5)

## 0.1.1 - 2022-07-12

## Added

- DRIFT-469: Initial implementation
- DRIFT-516: Add get_topic_data and deprecate get_list methods, [PR-3](https://github.com/panda-official/DriftPythonClient/pull/3)
