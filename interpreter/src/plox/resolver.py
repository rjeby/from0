from typing import TYPE_CHECKING
from src.plox.token import Token
from src.plox.token import Value
from src.plox.error import PloxError
from enum import Enum, auto
import src.plox.environment as env

if TYPE_CHECKING:
    from src.plox.expression import Expression


locals: dict["Expression", int] = {}


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver:
    scopes: list[dict[str, bool]] = []
    current_function = FunctionType.NONE
    current_class = ClassType.NONE

    @staticmethod
    def resolve_local(exp: "Expression", name: Token):
        n = len(Resolver.scopes)
        for depth in range(n):
            if name.lexeme in Resolver.scopes[n - 1 - depth]:
                locals[exp] = depth
                return

    @staticmethod
    def begin_scope():
        Resolver.scopes.append({})

    @staticmethod
    def end_scope():
        Resolver.scopes.pop()

    @staticmethod
    def define(name: Token):
        if not len(Resolver.scopes):
            return None
        top = Resolver.scopes[-1]
        top[name.lexeme] = True

    @staticmethod
    def declare(name: Token):
        if not len(Resolver.scopes):
            return None
        top = Resolver.scopes[-1]
        if name.lexeme in top:
            PloxError.error(name.line, "Variable Already Declared in this Scope")
            raise Exception("Variable Already Declared in this Scope")
        top[name.lexeme] = False

    @staticmethod
    def has_declaration_on_top(name: Token):
        if not len(Resolver.scopes):
            return None
        top = Resolver.scopes[-1]
        return name.lexeme in top and top[name.lexeme] == False

    @staticmethod
    def look_up_variable(name: Token, expr: "Expression"):
        distance = locals.get(expr, None)
        if distance != None:
            target = env.environment
            for _ in range(distance):
                assert target != None
                target = target.enclosing
            assert target != None
            return target.get(name)
        else:
            return env.globals.get(name)

    @staticmethod
    def look_up_super(expr: "Expression") -> list[Value]:
        distance = locals.get(expr, None)
        assert distance != None
        target = env.environment
        for _ in range(distance - 1):
            assert target != None
            target = target.enclosing
        assert target != None
        this = target.values["this"]
        assert this != None
        target = target.enclosing
        assert target != None
        super = target.values["super"]
        return [this, super]

    @staticmethod
    def assign_to_variable(name: Token, expr: "Expression", value: Value):
        distance = locals.get(expr, None)
        if distance != None:
            target = env.environment
            for _ in range(distance):
                assert target != None
                target = target.enclosing
            assert target != None
            target.define(name.lexeme, value)
        else:
            env.globals.define(name.lexeme, value)
