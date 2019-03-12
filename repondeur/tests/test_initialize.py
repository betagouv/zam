import pytest

from zam_repondeur.initialize import NotInitialized, needs_init


class P:
    def __init__(self) -> None:
        self.initialized = False

    def initialize(self, a: int, b: int) -> None:
        self.a = a
        self.b = b
        self.initialized = True

    @needs_init
    def f(self, x: int) -> int:
        return self.a * x + self.b


def test_cannot_call_f_before_initialization():
    p = P()
    with pytest.raises(NotInitialized):
        p.f(5)


def test_can_call_f_after_initialization():
    p = P()
    p.initialize(a=2, b=1)
    assert p.f(5) == 11
