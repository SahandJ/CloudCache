import collections.abc

import collections.abc
import inspect
from pathlib import Path
from typing import Callable, Any
from functools import partial

from urllib.parse import quote

key_mapper = Callable[[str, str, list[str], tuple[Any, ...], dict[str, Any]], str]


class CacheConfig:
    max_size: int = 128


def cloud_storage_key_mapper(file_name: str, func_name: str, func_args: list[str], *args, **kwargs):
    """ Key mapper for Google Cloud Storage

    Maps the function and it's arguments into the following format:
        <name-of-file>/<name-of-function>/<positional_arguments>@<keyword_arguments>

    where <positional_arguments> and <keyword_arguments> are comma-seperated in <key>=<value> format

    Args:
        file_name: name of file (e.g. 'main.py')
        func_name: name of function (e.g. 'fibonacci')
        func_args: function argument names
        *args: tuple of positional arguments
        **kwargs: dict of keyword arguments

    Returns:
        A string in the qualified format
    """

    quote_string = partial(quote, safe='')

    base = f'{file_name}/{func_name}'
    arg_items = '&'.join(f'{name}={quote_string(str(value))}' for name, value in zip(func_args, args))
    kwarg_items = '&'.join(f'{name}={quote_string(str(value))}' for name, value in sorted(kwargs.items()))
    return f'{base}/{arg_items}@{kwarg_items}'


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
