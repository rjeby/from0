from src.plox.callable import Callable
from src.plox.token import Value
from src.plox.token import Token
from src.plox.error import PloxError
from src.plox.function import Function


class Class(Callable):
    def __init__(
        self, name: str, methods: dict[str, Function], superclass: "Class | None" = None
    ):
        self.methods = methods
        self.superclass = superclass
        self.name = name

    def call(self, arguments: list[Value]) -> Value:
        instance = Instance(self)
        initializer = self.methods.get("init", None)
        if initializer:
            initializer.bind(instance).call(arguments)
        return instance

    def arity(self):
        initializer = self.methods.get("init", None)
        if initializer:
            return initializer.arity()
        return 0

    def find_method(self, name: Token) -> Function | None:
        if name.lexeme in self.methods:
            method = self.methods[name.lexeme]
            return method
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def __str__(self):
        return f"<class :: {self.name}>"


class Instance:
    def __init__(self, cls: Class):
        self.fields: dict[str, Value] = {}
        self.cls = cls

    def get(self, name: Token) -> Value:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.cls.find_method(name)
        if method:
            return method.bind(self)
        PloxError.error(name.line, "Undefined Property")
        raise Exception("Undefined Property")

    def set(self, name: Token, value: Value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<instance :: {self.cls.name}>"
