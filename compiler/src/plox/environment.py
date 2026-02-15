from src.plox.error import PloxError
from src.plox.token import Value
from src.plox.token import Token
from src.plox.callable import Clock


class Environment:
    def __init__(self, enclosing: "Environment | None" = None):
        self.enclosing = enclosing
        self.values: dict[str, Value] = {}

    def define(self, name: str, value: Value):
        self.values[name] = value

    def get(self, token: Token) -> Value:
        name = token.lexeme
        if name in self.values:
            return self.values[name]
        if self.enclosing != None:
            return self.enclosing.get(token)
        PloxError.error(token.line, "Undefined Variable")
        raise Exception("Undefined Variable")

    def assign(self, name: Token, value: Value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        PloxError.error(name.line, "Undefined Variable")
        raise Exception("Undefined Variable")


environment = Environment()
# Define clock native function in the global environment
environment.define("clock", Clock())
