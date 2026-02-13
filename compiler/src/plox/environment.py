from src.plox.error import PloxError
from src.plox.lexer import LiteralValue
from src.plox.token import Token


class Environment:
    def __init__(self, enclosing: "Environment | None" = None):
        self.enclosing = enclosing
        self.values: dict[str, LiteralValue] = {}

    def define(self, name: str, value: LiteralValue):
        self.values[name] = value

    def get(self, token: Token) -> LiteralValue:
        name = token.lexeme
        if name in self.values:
            return self.values[name]
        if self.enclosing != None:
            return self.enclosing.get(token)
        PloxError.error(token.line, "Undefined Variable")
        raise Exception("Undefined Variable")

    def assign(self, name: Token, value: LiteralValue):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        PloxError.error(name.line, "Undefined Variable")
        raise Exception("Undefined Variable")


environment = Environment()
