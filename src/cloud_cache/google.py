import collections.abc
import pickle
from io import BytesIO
from typing import Iterator
from datetime import datetime, timedelta

from google.cloud import storage

from . import CacheConfig


class CloudStorageCache(collections.abc.MutableMapping):

    def __init__(self, bucket: storage.Bucket, ttl: int, config: CacheConfig = None):
        self._bucket = bucket
        self._config = config
        self._ttl = ttl
        self._cache = dict()

    def __getitem__(self, key):
        # Check in-memory cache
        data = self._cache.get(key, None)
        if data is not None:
            return data

        # Check cloud storage bucket
        # TODO: Handle concurrency. Use lock?
        blob = self._bucket.get_blob(str(key))
        if blob is None:
            raise KeyError

        if datetime.fromisoformat(blob.metadata.get('expires_at')) <= datetime.now():
            data = pickle.loads(blob.download_as_bytes())
            self._cache[key] = data
            return data

        # blob.delete()
        raise KeyError

    def __setitem__(self, key, value):
        # TODO: Evict oldest item instead?
        if self._config and len(self._cache) >= self._config.max_size:
            raise ValueError('Cache has reached max size!')

        pickled_data = pickle.dumps(value)
        blob = self._bucket.blob(str(key))
        blob.metadata = {'expires_at': datetime.now().replace(microsecond=0) + timedelta(seconds=self._ttl)}
        if not blob.exists():
            blob.upload_from_file(BytesIO(pickled_data), size=len(pickled_data))

        self._cache[key] = value

    def __delitem__(self, __v) -> None:
        # TODO
        pass

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> Iterator:
        yield from self._cache.items()


class DatastoreCache(collections.abc.MutableMapping):
    def __setitem__(self, __k, __v) -> None:
        pass

    def __delitem__(self, __v) -> None:
        pass

    def __getitem__(self, __k):
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator:
        pass
