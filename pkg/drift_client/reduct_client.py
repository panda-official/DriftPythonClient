"""Reduct Storage client"""

import asyncio
from asyncio import new_event_loop
from typing import Tuple, List, Optional, Dict, Iterator

from reduct import Client, Bucket, ReductError, EntryInfo

from drift_client.error import DriftClientError


class ReductStoreClient:
    """Wrapper around ReductStore client"""

    def __init__(self, url: str, token: str, timeout: float, loop=None):
        """
        Args:
            url: ReductStore URL
            token: ReductStore API token
            loop: asyncio event loop
        """
        self._client = Client(url, api_token=token, timeout=timeout)
        self._bucket = "data"
        self._loop = loop if loop else new_event_loop()
        _ = self._run(self._client.info())  # check connection for fallback to Minio

    def check_package_list(self, package_names: List[str]) -> list:
        """Check if packages exist in Reduct Storage"""
        entry_map: Dict[str, List[int]] = {}
        # bad design, we don't know if all packages belong to the same entry
        for package_name in package_names:
            entry, timestamp = self._parse_minio_path(package_name)
            if entry not in entry_map:
                entry_map[entry] = [timestamp]
            else:
                entry_map[entry].append(timestamp)

        # retrieve all entries
        try:
            bucket: Bucket = self._run(self._client.get_bucket(self._bucket))
            entries_in_storage: List[EntryInfo] = self._run(bucket.get_entry_list())
        except ReductError as err:
            raise DriftClientError("Failed to list entries") from err

        # check if the packages are still in storage
        for entry in entries_in_storage:
            if entry.name in entry_map:
                entry_map[entry.name] = sorted(
                    timestamp
                    for timestamp in entry_map[entry.name]
                    if entry.oldest_record <= timestamp * 1000 <= entry.latest_record
                )

        # remove not existing topics
        for entry in list(entry_map.keys()):
            if entry not in [e.name for e in entries_in_storage]:
                del entry_map[entry]

        # restore entry/ts.db format
        return [
            f"{entry}/{timestamp}.dp"
            for entry, timestamps in entry_map.items()
            for timestamp in timestamps
        ]

    def fetch_data(self, path: str) -> Optional[bytes]:
        """Fetch data from Reduct Storage via timestamp"""
        entry, timestamp = self._parse_minio_path(path)
        try:
            return self._run(self._read_by_timestamp(entry, timestamp))
        except ReductError as err:
            raise DriftClientError(f"Could not read item at {path}") from err

    def walk(self, entry: str, start: int, stop: int, **kwargs) -> Iterator[bytes]:
        """
        Walk through the records of an entry between start and stop.
        Args:
            entry: entry name
            start: start timestamp UNIX in seconds
            stop: stop timestamp UNIX in seconds
        Keyword Args:
            ttl: time to live for the query
        Raises:
            DriftClientError: if failed to fetch data
        """

        bucket: Bucket = self._run(self._client.get_bucket(self._bucket))

        ttl = kwargs.get("ttl", 60)
        ait = bucket.query(entry, start * 1000_000, stop * 1000_000, ttl=ttl)

        async def get_next():
            try:
                pkg = await ait.__anext__()  # pylint: disable=unnecessary-dunder-call
                return await pkg.read_all()
            except StopAsyncIteration:
                return None

        try:
            while True:
                pkg = self._run(get_next())
                if pkg is None:
                    break
                yield pkg
        except ReductError as err:
            raise DriftClientError(
                f"Failed to fetch data from {entry}: {err.message}"
            ) from err

    def name(self) -> str:
        """Return name of the client"""
        return "reductstore"

    async def _read_by_timestamp(self, entry: str, timestamp: int) -> bytes:
        bucket: Bucket = await self._client.get_bucket(self._bucket)
        async with bucket.read(entry, timestamp * 1000) as record:
            return await record.read_all()

    @staticmethod
    def _parse_minio_path(path: str) -> Tuple[str, int]:
        entry, file = path.split("/")
        return entry, int(file.replace(".dp", ""))

    def _run(self, coro):
        if self._loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, self._loop).result()
        return self._loop.run_until_complete(coro)
