from src.plox.token import TokenType
from src.plox.token import Token
from src.plox.token import LiteralValue


class Expression:
    def __init__(self, x: int):
        self.x = x

    def evaluate(self) -> LiteralValue:
        pass


class Literal(Expression):
    def __init__(self, literal: LiteralValue):
        self.literal = literal

    def __str__(self):
        if self.literal == None:
            return "nil"
        return str(self.literal)

    def evaluate(self) -> LiteralValue:
        return self.literal


class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"({str(self.left)} {self.operator.lexeme} {str(self.right)})"

    def evaluate(self) -> LiteralValue:
        left = self.left.evaluate()
        right = self.right.evaluate()
        if left == None or right == None:
            # TODO: Handle Dynamic Typing
            return None
        match self.operator.type:
            case TokenType.MINUS:
                return float(left) - float(right)
            case TokenType.STAR:
                return float(left) * float(right)
            case TokenType.SLASH:
                # TODO: Check for zero division
                return float(left) / float(right)
            case TokenType.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                return float(left) + float(right)
            case TokenType.GREATER:
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                return float(left) >= float(right)
            case TokenType.LESS:
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                return float(left) <= float(right)
            case TokenType.EQUAL_EQUAL:
                return type(left) == type(right) and left == right
            case TokenType.BANG_EQUAL:
                return type(left) != type(right) or left != right
            case _:
                raise Exception("Unexpected Operator")


class Unary(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"({self.operator.lexeme} {str(self.right)})"

    def evaluate(self) -> LiteralValue:
        right = self.right.evaluate()
        match self.operator.type:
            case TokenType.MINUS:
                if right == None:
                    # TODO: Handle Dynamic Typing
                    return None
                return -float(right)
            case TokenType.BANG:
                if right == None or (isinstance(right, bool) and right == False):
                    return True
                return False
            case _:
                raise Exception("Unexpected Operator")


class Grouping(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __str__(self):
        return f"(group {str(self.expression)})"

    def evaluate(self) -> LiteralValue:
        return self.expression.evaluate()
