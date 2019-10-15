from abc import ABC, abstractmethod


class Command(ABC):
    def __call__(self, ctx, *args, **kwargs):
        method = self.dispatch(ctx)
        if kwargs.pop("log", True):
            msg_template = self._find_msg_template(method)
            self.log(msg_template, *args, **kwargs)
        return method(ctx, *args, **kwargs)

    @abstractmethod
    def dispatch(self, ctx):
        raise NotImplementedError

    def log(self, msg_template, *args, **kwargs):
        if msg_template:
            msg = msg_template.strip().format(*args, **kwargs)
            print(f"\033[92m--- {msg} ---\033[0m")

    def _find_msg_template(self, method):
        method_msg = method.__doc__
        class_msg = self.__class__.__doc__
        return method_msg or class_msg


class SimpleCommand(Command):
    def __init__(self, func):
        self.func = func

    def dispatch(self, ctx):
        return self.func


def command(func):
    return SimpleCommand(func)
