from src.plox.token import Token
from src.plox.expression import Expression
from src.plox.lexer import LiteralValue


class Statement:
    def __init__(self):
        pass

    def execute(self):
        pass


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        self.expression.evaluate()


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        print(self.stringify(self.expression.evaluate()))

    @staticmethod
    def stringify(literal: LiteralValue):
        if literal == None:
            return "nil"
        if isinstance(literal, bool):
            return "true" if literal else "false"
        if isinstance(literal, float):
            text = str(literal)
            return text[:-2] if text.endswith(".0") else text
        return str(literal)


class VarDeclarationStatement(Statement):
    def __init__(self, token: Token, initializer: Expression | None):
        self.token = token
        self.initializer = initializer

    def execute(self):
        # TODO
        pass
