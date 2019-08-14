from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # let mypy think that @reify is like a @property
    reify = property
else:
    from pyramid.decorator import reify  # noqa
