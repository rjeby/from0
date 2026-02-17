from src.plox.callable import Callable
from src.plox.token import Value
from src.plox.token import Token
from src.plox.error import PloxError


class Class(Callable):
    def __init__(self, name: str):
        self.name = name

    def call(self, arguments: list[Value]) -> Value:
        instance = Instance(self)
        return instance

    def arity(self):
        return 0

    def __str__(self):
        return f"<class :: {self.name}>"


class Instance:
    def __init__(self, cls: Class):
        self.fields: dict[str, Value] = {}
        self.cls = cls

    def get(self, name: Token) -> Value:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        PloxError.error(name.line, "Undefined Property")
        raise Exception("Undefined Property")

    def set(self, name: Token, value: Value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<instance :: {self.cls.name}>"
