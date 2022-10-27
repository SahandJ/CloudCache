poeimport collections.abc
import inspect
from pathlib import Path
from typing import Callable, Any

key_mapper = Callable[[str, str, list[str], tuple[Any, ...], dict[str, Any]], str]


def cached(cache: collections.abc.MutableMapping, key: key_mapper):
    def decorator(func):
        def wrapper(*args, **kwargs):
            k = key(
                Path(inspect.getfile(func)).name,  # name of the current file
                func.__name__,  # name of the cached function
                inspect.getfullargspec(func).args,  # arguments of the cached function
                *args,
                **kwargs
            )
            try:
                return cache[k]
            except KeyError:
                pass  # key not found
            v = func(*args, **kwargs)
            try:
                cache[k] = v
            except ValueError:
                pass  # value too large
            return v

        return wrapper

    return decorator
