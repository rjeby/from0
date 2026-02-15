from src.plox.token import Token
from src.plox.expression import Expression
from src.plox.token import Value
from src.plox.function import Function
from src.plox.ret import Return
import src.plox.environment as env


class Statement:
    def __init__(self):
        pass

    def execute(self):
        pass


class ReturnStatement(Statement):
    def __init__(self, keyword: Token, value: Expression | None):
        self.keyword = keyword
        self.value = value

    def execute(self):
        value = None
        if self.value != None:
            value = self.value.evaluate()
        raise Return(value)


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        self.expression.evaluate()


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body

    def execute(self):
        while self.is_truthy(self.condition.evaluate()):
            self.body.execute()

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

    @staticmethod
    def is_truthy(value: Value):
        if value == None or (isinstance(value, bool) and value == False):
            return False
        return True


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


class FuncDeclarationStatement(Statement):
    def __init__(self, name: Token, params: list[Token], body: BlockStatement):
        self.name = name
        self.params = params
        self.body = body

    def execute(self):
        callable = Function(env.environment, self)
        env.environment.define(self.name.lexeme, callable)


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        print(self.stringify(self.expression.evaluate()))

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
