from src.plox.callable import Callable
from src.plox.ret import Return
from typing import TYPE_CHECKING
from src.plox.token import Value
import src.plox.environment as env


if TYPE_CHECKING:
    from src.plox.statement import FuncDeclarationStatement
    from src.plox.cls import Instance


class Function(Callable):
    def __init__(
        self, closure: env.Environment, declaration: "FuncDeclarationStatement"
    ):
        self.closure = closure
        self.declaration = declaration

    def bind(self, instance: "Instance"):
        environment = env.Environment(self.closure)
        environment.define("this", instance)
        return Function(environment, self.declaration)

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, arguments: list[Value]):
        previous = env.environment
        try:
            env.environment = env.Environment(self.closure)
            for index in range(len(arguments)):
                env.environment.define(
                    self.declaration.params[index].lexeme, arguments[index]
                )

            self.declaration.body.execute()
        except Return as ret:
            return ret.value

        finally:
            env.environment = previous

        return None

    def __str__(self) -> str:
        return f"<fn :: {self.declaration.name.lexeme}>"
