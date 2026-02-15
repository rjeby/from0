from src.plox.callable import Callable
from typing import TYPE_CHECKING
from src.plox.token import Value
import src.plox.environment as env


if TYPE_CHECKING:
    from src.plox.statement import FuncDeclarationStatement


class Function(Callable):
    def __init__(self, declaration: "FuncDeclarationStatement"):
        self.declaration = declaration

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, arguments: list[Value]):
        env.environment = env.Environment(env.environment)
        for index in range(len(arguments)):
            env.environment.define(
                self.declaration.params[index].lexeme, arguments[index]
            )
        self.declaration.body.execute()
        env.environment = env.environment.enclosing

        return None

    def __str__(self) -> str:
        return f"<fn :: {self.declaration.name.lexeme}>"
