import collections.abc
import inspect
from pathlib import Path


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
    base = f'{file_name}/{func_name}'
    arg_items = '&'.join(f'{name}={value}' for name, value in zip(func_args, args))
    kwarg_items = '&'.join(f'{name}={value}' for name, value in sorted(kwargs.items()))
    return f'{base}/{arg_items}@{kwarg_items}'
