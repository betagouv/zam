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
