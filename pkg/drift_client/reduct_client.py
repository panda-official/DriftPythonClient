"""Reduct Storage client"""
from typing import Tuple, List, Optional

from drift_client.error import DriftClientError
from reduct import Client, Bucket, ReductError, EntryInfo
from asyncio import new_event_loop


class ReductStorageClient:
    def __init__(self, url: str, token: str):
        self._client = Client(url, api_token=token)
        self._bucket = "data"
        self._loop = new_event_loop()
        _ = self._run(self._client.info())  # check connection for fallback to Minio

    def check_package_list(self, package_names: List[str]) -> list:
        """Check if packages exist in Reduct Storage"""
        entry_map = dict()
        for package_name in package_names:
            entry, timestamp = self._parse_minio_path(package_name)
            if entry not in entry_map:
                entry_map[entry] = [timestamp]
            else:
                entry_map[entry].append(timestamp)

        try:
            bucket: Bucket = self._run(self._client.get_bucket(self._bucket))
            entries_in_storage: List[EntryInfo] = self._run(bucket.get_entry_list())
        except ReductError as err:
            raise DriftClientError(f"Failed to list entries") from err

        for entry in entries_in_storage:
            if entry.name in entry_map:
                entry_map[entry.name] = sorted(
                    timestamp
                    for timestamp in entry_map[entry.name]
                    if entry.oldest_record <= timestamp * 1000 <= entry.latest_record
                )

        return [
            "{}/{}.dp".format(entry, timestamp)
            for entry, timestamps in entry_map.items()
            for timestamp in timestamps
        ]

    def fetch_data(self, path: str) -> Optional[bytes]:
        entry, timestamp = self._parse_minio_path(path)
        try:
            return self._run(self._read_by_timestamp(entry, timestamp))
        except ReductError as err:
            raise DriftClientError(f"Could not read item at {path}") from err

    async def _read_by_timestamp(self, entry: str, timestamp: int) -> bytes:
        bucket: Bucket = await self._client.get_bucket(self._bucket)
        async with bucket.read(entry, timestamp * 1000) as record:
            return await record.read_all()

    @staticmethod
    def _parse_minio_path(path: str) -> Tuple[str, int]:
        entry, file = path.split("/")
        return entry, int(file.replace(".dp", ""))

    def _run(self, coro):
        return self._loop.run_until_complete(coro)
