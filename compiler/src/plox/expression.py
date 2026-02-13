from src.plox.error import PloxError
from src.plox.token import TokenType
from src.plox.token import Token
from src.plox.token import LiteralValue
import src.plox.environment as env


class Expression:
    def __init__(self):
        pass

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


class Variable(Expression):
    def __init__(self, name: Token):
        self.name = name

    def __str__(self):
        return str(self.name.lexeme)

    def evaluate(self) -> LiteralValue:
        return env.environment.get(self.name)


class Assignment(Expression):

    def __init__(self, name: Token, value: Expression):
        self.name = name
        self.value = value

    def __str__(self):
        return f"({self.name.lexeme} = {str(self.value)})"

    def evaluate(self):
        value = self.value.evaluate()
        env.environment.assign(self.name, value)
        return value


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
        match self.operator.type:
            case TokenType.MINUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) - float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.STAR:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) * float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.SLASH:
                # TODO: Check for zero division
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) / float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                PloxError.error(
                    self.operator.line, "Operands must be Numbers or Strings"
                )
                raise Exception("Operands must be Numbers or Strings")
            case TokenType.GREATER:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) > float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.GREATER_EQUAL:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) >= float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.LESS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) < float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.LESS_EQUAL:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) <= float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.EQUAL_EQUAL:
                return type(left) == type(right) and left == right
            case TokenType.BANG_EQUAL:
                return type(left) != type(right) or left != right
            case _:
                PloxError.error(self.operator.line, "Unexpected Operator")
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
                if isinstance(right, float):
                    return -float(right)
                PloxError.error(self.operator.line, "Operand must be a Number")
                raise Exception("Operand must be a Number")
            case TokenType.BANG:
                if right == None or (isinstance(right, bool) and right == False):
                    return True
                return False
            case _:
                PloxError.error(self.operator.line, "Unexpected Operator")
                raise Exception("Unexpected Operator")


class Grouping(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __str__(self):
        return f"(group {str(self.expression)})"

    def evaluate(self) -> LiteralValue:
        return self.expression.evaluate()
