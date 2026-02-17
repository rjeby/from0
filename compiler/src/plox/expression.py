from src.plox.error import PloxError
from src.plox.token import TokenType
from src.plox.token import Token
from src.plox.token import LiteralValue
from src.plox.token import Value
from src.plox.callable import Callable
from src.plox.resolver import Resolver
from src.plox.resolver import ClassType
from src.plox.cls import Class
from src.plox.cls import Instance



class Expression:
    def __init__(self):
        pass

    def evaluate(self) -> Value:
        pass

    def resolve(self):
        pass


class SetExpression(Expression):
    def __init__(self, object: Expression, name: Token, value: Expression):
        self.object = object
        self.name = name
        self.value = value

    def evaluate(self) -> Value:
        object = self.object.evaluate()
        if not isinstance(object, Instance):
            PloxError.error(self.name.line, "Only Instances Have Fields")
            raise Exception("Only Instances Have Fields")
        value = self.value.evaluate()
        object.set(self.name, value)
        return value

    def resolve(self):
        self.object.resolve()
        self.value.resolve()


class GetExpression(Expression):
    def __init__(self, object: Expression, name: Token):
        self.object = object
        self.name = name

    def evaluate(self) -> Value:
        object = self.object.evaluate()
        if not isinstance(object, Instance):
            PloxError.error(self.name.line, "Only Instances Have Properties")
            raise Exception("Only Instances Have Properties")
        return object.get(self.name)

    def resolve(self):
        self.object.resolve()


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

    def resolve(self):
        self.callee.resolve()
        for argument in self.arguments:
            argument.resolve()


class Literal(Expression):
    def __init__(self, literal: LiteralValue):
        self.literal = literal

    def __str__(self):
        if self.literal == None:
            return "nil"
        return str(self.literal)

    def evaluate(self) -> LiteralValue:
        return self.literal

    def resolve(self):
        return


class Super(Expression):
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def evaluate(self):
        this, superclass = Resolver.look_up_super(self)
        assert isinstance(superclass, Class)
        assert isinstance(this, Instance)
        method = superclass.find_method(self.method)
        if not method:
            PloxError.error(self.method.line, "Undefined Method")
            raise Exception("Undefined Method")
        return method.bind(this)

    def resolve(self):
        if Resolver.current_class != ClassType.SUBCLASS:
            PloxError.error(self.keyword.line, "Super can only be used in Subclass")
            raise Exception("Super can only be used in Subclass")
        Resolver.resolve_local(self, self.keyword)


class This(Expression):
    def __init__(self, keyword: Token):
        self.keyword = keyword

    def evaluate(self):
        return Resolver.look_up_variable(self.keyword, self)

    def resolve(self):
        if Resolver.current_class != ClassType.CLASS and Resolver.current_class != ClassType.SUBCLASS:
            PloxError.error(self.keyword.line, "This cannot be used outside a Class")
            raise Exception("This cannot be used outside a Class")

        Resolver.resolve_local(self, self.keyword)


class Variable(Expression):
    def __init__(self, name: Token):
        self.name = name

    def __str__(self):
        return str(self.name.lexeme)

    def evaluate(self) -> Value:
        return Resolver.look_up_variable(self.name, self)

    def resolve(self):
        if Resolver.has_declaration_on_top(self.name):
            PloxError.error(self.name.line, "Can't Read Local Variable in Initializer")
            raise Exception("Can't Read Local Variable in Initializer")
        Resolver.resolve_local(self, self.name)


class Assignment(Expression):

    def __init__(self, name: Token, value: Expression):
        self.name = name
        self.value = value

    def __str__(self):
        return f"({self.name.lexeme} = {str(self.value)})"

    def evaluate(self):
        value = self.value.evaluate()
        Resolver.assign_to_variable(self.name, self, value)
        return value

    def resolve(self):
        self.value.resolve()
        Resolver.resolve_local(self, self.name)


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

    def resolve(self):
        self.left.resolve()
        self.right.resolve()

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

    def resolve(self):
        self.right.resolve()


class Grouping(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __str__(self):
        return f"(group {str(self.expression)})"

    def evaluate(self) -> Value:
        return self.expression.evaluate()

    def resolve(self):
        self.expression.resolve()
