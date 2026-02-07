from src.plox.token import Token
from src.plox.token import LiteralValue


class Expression:
    def __init__(self, x: int):
        self.x = x


class Literal(Expression):
    def __init__(self, literal: LiteralValue):
        self.literal = literal

    def __str__(self):
        if not self.literal:
            return "nil"
        return str(self.literal)


class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"({str(self.left)} {self.operator.lexeme} {str(self.right)})"


class Unary(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"({self.operator.lexeme} {str(self.right)})"


class Grouping(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __str__(self):
        return f"(group {str(self.expression)})"
