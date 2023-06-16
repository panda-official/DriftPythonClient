# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added:

- DRIFT-613: `Client.walk` method to iterate data in blob storage, [PR-32](https://github.com/panda-official/DriftPythonClient/pull/32)


### Changed:

- Migrate to pyproject.toml, [PR-33](https://github.com/panda-official/DriftPythonClient/pull/33)

## 0.5.0 - 2023-04-06

### Changed

- Switch to wavelet buffer 0.6.0, [PR-31](https://github.com/panda-official/DriftPythonClient/pull/31)

## 0.4.1 - 2023-02-21

### Fixed:

- Empty password and error message when no ReductStore available, [PR-30](https://github.com/panda-official/DriftPythonClient/pull/30)

## 0.4.0 - 2023-02-13

### Added:

- DRIFT-542: Quick start manual for Windows users, [PR-27](https://github.com/panda-official/DriftPythonClient/pull/27)
- ISSUE-88: `loop` parameter for `DriftClient` constructor to integrate into existing even
  loop, [PR-29](https://github.com/panda-official/DriftPythonClient/pull/29)

### 0.3.1 - 2022-12-01

### Fixed:

- Circular import in protobuf files, [PR-25](https://github.com/panda-official/DriftPythonClient/pull/25)

### 0.3.0 - 2022-11-23

### Added

- DRIFT-534: Dependencies compatibility table, [PR-21](https://github.com/panda-official/DriftPythonClient/pull/21)
- DRIFT-550: DriftClientError class, to catch (initially) Minio
  errors, [PR-16](https://github.com/panda-official/DriftPythonClient/pull/16)
- DRIFT-563: Reduct Storage client, [PR-24](https://github.com/panda-official/DriftPythonClient/pull/24)
- DRIFT-604: Add blob property to DriftDataPackage, [PR-20](https://github.com/panda-official/DriftPythonClient/pull/20)

### Fixed:

- DRIFT-603: Status check for DriftDataPackage, [PR-23](https://github.com/panda-official/DriftPythonClient/pull/23)

## 0.2.1 - 2922-09-09

### Added

- DRIFT-473: Add tutorial and `PANDA|Drift` page, [PR-12](https://github.com/panda-official/DriftPythonClient/pull/12)
-
Add `Denoising timeseries data by using WaveletBuffer`, [PR-12](https://github.com/panda-official/DriftPythonClient/pull/12)
- DRIFT-587: Add _Drift Core_ on diagram, [PR-17](https://github.com/panda-official/DriftPythonClient/pull/17)

### Fixed

- DRIFT-545: Build on Apple M1, [PR-15](https://github.com/panda-official/DriftPythonClient/pull/15)

## 0.2.0 - 2022-08-16

### Added

- DRIFT-478: `Client.get_metrics` to get metrics from
  InfluxDB, [PR-10](https://github.com/panda-official/DriftPythonClient/pull/10)
- DRIFT-510: Make package paths by using time from
  InfluxDB, [PR-2](https://github.com/panda-official/DriftPythonClient/pull/2)
- DRIFT-516: `Client.get_topic_data` to get paths in
  Minio, [PR-5](https://github.com/panda-official/DriftPythonClient/pull/5)

### Deprecated

- DRIFT-516: `Client.get_list`. Remove in 1.0.0, [PR-5](https://github.com/panda-official/DriftPythonClient/pull/5)

## 0.1.1 - 2022-07-12

## Added

- DRIFT-469: Initial implementation
- DRIFT-516: Add get_topic_data and deprecate get_list
  methods, [PR-3](https://github.com/panda-official/DriftPythonClient/pull/3)
