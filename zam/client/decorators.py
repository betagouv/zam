import os
from pathlib import Path
from typing import Callable, List

import wrapt
from logbook import warn


@wrapt.decorator
def check_existence(
        wrapped: Callable, instance: None,
        args: List[Path], kwargs: dict) -> str:
    if not args[0].exists():
        warn(f'Missing {args[0]}')
        return ''
    return wrapped(*args, **kwargs)


def require_env_vars(env_vars: list) -> Callable:
    @wrapt.decorator
    def wrapper(
            wrapped: Callable, instance: None,
            args: List[Path], kwargs: dict) -> str:
        values = []
        for env_var in env_vars:
            try:
                values.append(os.environ[env_var])
            except KeyError:
                raise Exception(f'Please set {env_var} environment variables.')
        return wrapped(*values + list(args), **kwargs)
    return wrapper
