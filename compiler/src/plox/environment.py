from src.plox.error import PloxError
from src.plox.lexer import LiteralValue
from src.plox.token import Token


class Environment:
    def __init__(self):
        self.values: dict[str, LiteralValue] = {}

    def define(self, name: str, value: LiteralValue):
        self.values[name] = value

    def get(self, token: Token):
        name = token.lexeme
        if name in self.values:
            return self.values[name]
        PloxError.error(token.line, "Undefined Variable")
        raise Exception("Undefined Variable")


environment = Environment()
