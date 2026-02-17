from src.plox.token import Token
from src.plox.expression import Expression
from src.plox.token import Value
from src.plox.function import Function
from src.plox.ret import Return
from src.plox.resolver import ClassType
from src.plox.resolver import FunctionType
from src.plox.resolver import Resolver
from src.plox.error import PloxError
from src.plox.cls import Class
import src.plox.environment as env


class Statement:
    def __init__(self):
        pass

    def execute(self):
        pass

    def resolve(self):
        pass


class BlockStatement(Statement):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def execute(self):
        try:
            env.environment = env.Environment(env.environment)
            for statement in self.statements:
                statement.execute()
        finally:
            # Reset the environement even if an exception is thrown (REPL ...)
            env.environment = env.environment.enclosing

    def resolve(self):
        Resolver.begin_scope()
        for statement in self.statements:
            statement.resolve()
        Resolver.end_scope()


class FuncDeclarationStatement(Statement):
    def __init__(self, name: Token, params: list[Token], body: BlockStatement):
        self.name = name
        self.params = params
        self.body = body

    def execute(self):
        callable = Function(env.environment, self)
        env.environment.define(self.name.lexeme, callable)

    def resolve(self):
        enclosing = Resolver.current_function
        Resolver.current_function = FunctionType.FUNCTION
        Resolver.declare(self.name)
        Resolver.define(self.name)
        Resolver.begin_scope()
        for param in self.params:
            Resolver.declare(param)
            Resolver.define(param)
        self.body.resolve()
        Resolver.end_scope()
        Resolver.current_function = enclosing


class ClassDeclarationStatement(Statement):
    def __init__(self, name: Token, methods: list[FuncDeclarationStatement]):
        self.name = name
        self.methods = methods

    def execute(self):
        env.environment.define(self.name.lexeme, None)
        methods: dict[str, Function] = {}
        for method in self.methods:
            methods[method.name.lexeme] = Function(env.environment, method)
        cls = Class(self.name.lexeme, methods)
        env.environment.assign(self.name, cls)

    def resolve(self):
        enclosing_class = Resolver.current_class
        Resolver.current_class = ClassType.CLASS
        Resolver.declare(self.name)
        Resolver.begin_scope()
        Resolver.scopes[-1]["this"] = True
        for method in self.methods:
            enclosing_function = Resolver.current_function
            Resolver.current_function = FunctionType.METHOD
            Resolver.declare(method.name)
            Resolver.define(method.name)
            Resolver.begin_scope()
            for param in method.params:
                Resolver.declare(param)
                Resolver.define(param)
            method.body.resolve()
            Resolver.end_scope()
            Resolver.current_function = enclosing_function
        Resolver.end_scope()
        Resolver.define(self.name)
        Resolver.current_class = enclosing_class


class ReturnStatement(Statement):
    def __init__(self, keyword: Token, value: Expression | None):
        self.keyword = keyword
        self.value = value

    def execute(self):
        value = None
        if self.value != None:
            value = self.value.evaluate()
        raise Return(value)

    def resolve(self):
        if Resolver.current_function == FunctionType.NONE:
            PloxError.error(self.keyword.line, "Invalid Return Statement")
            raise Exception("Invalid Return Statement")

        if self.value:
            self.value.resolve()


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        self.expression.evaluate()

    def resolve(self):
        self.expression.resolve()


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body

    def execute(self):
        while self.is_truthy(self.condition.evaluate()):
            self.body.execute()

    def resolve(self):
        self.condition.resolve()
        self.body.resolve()

    @staticmethod
    def is_truthy(value: Value):
        if value == None or (isinstance(value, bool) and value == False):
            return False
        return True


class IfStatement(Statement):
    def __init__(
        self,
        condition: Expression,
        then_branch: Statement,
        else_branch: Statement | None = None,
    ):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def execute(self):
        if self.is_truthy(self.condition.evaluate()):
            self.then_branch.execute()
        elif self.else_branch != None:
            self.else_branch.execute()

    def resolve(self):
        self.condition.resolve()
        self.then_branch.resolve()
        if self.else_branch:
            self.else_branch.resolve()

    @staticmethod
    def is_truthy(value: Value):
        if value == None or (isinstance(value, bool) and value == False):
            return False
        return True


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        print(self.stringify(self.expression.evaluate()))

    def resolve(self):
        self.expression.resolve()

    @staticmethod
    def stringify(literal: Value):
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
        name = self.token.lexeme
        value = None
        if self.initializer != None:
            value = self.initializer.evaluate()
        env.environment.define(name, value)

    def resolve(self):
        Resolver.declare(self.token)
        if self.initializer:
            self.initializer.resolve()
        Resolver.define(self.token)
