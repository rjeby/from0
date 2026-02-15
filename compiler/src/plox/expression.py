from src.plox.error import PloxError
from src.plox.token import TokenType
from src.plox.token import Token
from src.plox.token import LiteralValue
from src.plox.token import Value
from src.plox.callable import Callable
import src.plox.environment as env


class Expression:
    def __init__(self):
        pass

    def evaluate(self) -> Value:
        pass


class CallExpression(Expression):
    def __init__(self, callee: Expression, paren: Token, arguments: list[Expression]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def evaluate(self):
        function = self.callee.evaluate()
        if not isinstance(function, Callable):
            PloxError.error(self.paren.line, "Callee must be a Callable")
            raise Exception("Callee must be a Callable")
        if function.arity() != len(self.arguments):
            PloxError.error(self.paren.line, "Invalid Argument Count")
            raise Exception("Invalid Argument Count")
        arguments = [arg.evaluate() for arg in self.arguments]
        return function.call(arguments)


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

    def evaluate(self) -> Value:
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

    def evaluate(self) -> Value:
        match self.operator.type:
            case TokenType.MINUS:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) - float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.STAR:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) * float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.SLASH:
                left = self.left.evaluate()
                right = self.right.evaluate()
                # TODO: Check for zero division
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) / float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.PLUS:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                PloxError.error(
                    self.operator.line, "Operands must be Numbers or Strings"
                )
                raise Exception("Operands must be Numbers or Strings")
            case TokenType.GREATER:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) > float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.GREATER_EQUAL:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) >= float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.LESS:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) < float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.LESS_EQUAL:
                left = self.left.evaluate()
                right = self.right.evaluate()
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) <= float(right)
                PloxError.error(self.operator.line, "Operands must be Numbers")
                raise Exception("Operands must be Numbers")
            case TokenType.EQUAL_EQUAL:
                left = self.left.evaluate()
                right = self.right.evaluate()
                return type(left) == type(right) and left == right
            case TokenType.BANG_EQUAL:
                left = self.left.evaluate()
                right = self.right.evaluate()
                return type(left) != type(right) or left != right
            case TokenType.OR:
                left = self.left.evaluate()
                if self.is_truthy(left):
                    return left
                return self.right.evaluate()
            case TokenType.AND:
                left = self.left.evaluate()
                if not self.is_truthy(left):
                    return left
                return self.right.evaluate()
            case _:
                PloxError.error(self.operator.line, "Unexpected Operator")
                raise Exception("Unexpected Operator")

    @staticmethod
    def is_truthy(value: Value):
        if value == None or (isinstance(value, bool) and value == False):
            return False
        return True


class Unary(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"({self.operator.lexeme} {str(self.right)})"

    def evaluate(self) -> Value:
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

    def evaluate(self) -> Value:
        return self.expression.evaluate()
