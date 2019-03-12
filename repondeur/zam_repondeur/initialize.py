from functools import wraps

from typing import Any, Callable, TypeVar, cast


class NotInitialized(Exception):
    pass


F = TypeVar("F", bound=Callable)


def needs_init(func: F) -> F:
    """Decorator for methods that require the object to be initialized"""

    @wraps(func)
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not self.initialized:
            raise NotInitialized
        return func(self, *args, **kwargs)

    return cast(F, wrapped)
