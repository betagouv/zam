import wrapt
from logbook import warn


@wrapt.decorator
def check_existence(wrapped, instance, args, kwargs):
    if not args[0].exists():
        warn(f'Missing {args[0]}')
        return ''
    return wrapped(*args, **kwargs)
