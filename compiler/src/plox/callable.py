from time import time
from src.plox.token import Value


class Callable:
    def arity(self) -> int:
        return 0

    def call(self, arguments: list[Value]) -> Value:
        pass

    def __str__(self) -> str:
        return ""


class Clock(Callable):

    def arity(self):
        return 0

    def call(self, arguments: list[Value]):
        return time()

    def __str__(self):
        return "<native fn :: clock>"
