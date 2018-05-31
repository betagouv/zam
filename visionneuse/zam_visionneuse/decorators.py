import os
from pathlib import Path
from typing import Any, Callable, List

import wrapt
from logbook import warn


@wrapt.decorator
def check_existence(
    wrapped: Callable, instance: None, args: List[Path], kwargs: dict
) -> str:
    if not args[0].exists():
        warn(f"Missing {args[0]}")
        return ""
    return wrapped(*args, **kwargs)


def require_env_vars(env_vars: list) -> Callable:
    @wrapt.decorator
    def wrapper(
        wrapped: Callable, instance: None, args: List[Path], kwargs: dict
    ) -> Any:
        for env_var in env_vars:
            assert (
                env_var in os.environ
            ), f"Please set {env_var} environment variable."
        return wrapped(*args, **kwargs)

    return wrapper
