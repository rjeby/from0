from src.plox.expression import Literal
from src.plox.expression import Expression
from src.plox.expression import Binary
from src.plox.expression import Unary
from src.plox.expression import Grouping
from src.plox.token import Token
from src.plox.token import TokenType
from src.plox.error import PloxError


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse_expression(self) -> Expression:
        return self.parse_equality()

    def parse_equality(self):
        expression = self.parse_comparison()
        while (
            self.peek().type == TokenType.BANG_EQUAL
            or self.peek().type == TokenType.EQUAL_EQUAL
        ):
            token = self.consume()
            right = self.parse_comparison()
            expression = Binary(expression, token, right)
        return expression

    def parse_comparison(self):
        expression = self.parse_term()
        while (
            self.peek().type == TokenType.GREATER
            or self.peek().type == TokenType.GREATER_EQUAL
            or self.peek().type == TokenType.LESS
            or self.peek().type == TokenType.LESS_EQUAL
        ):
            token = self.consume()
            right = self.parse_term()
            expression = Binary(expression, token, right)
        return expression

    def parse_term(self):
        expression = self.parse_factor()
        while self.peek().type == TokenType.MINUS or self.peek().type == TokenType.PLUS:
            token = self.consume()
            right = self.parse_factor()
            expression = Binary(expression, token, right)
        return expression

    def parse_factor(self):
        expression = self.parse_unary()
        while self.peek().type == TokenType.SLASH or self.peek().type == TokenType.STAR:
            token = self.consume()
            right = self.parse_unary()
            expression = Binary(expression, token, right)
        return expression

    def parse_unary(self) -> Expression:
        token = self.peek()
        type = token.type
        if type == TokenType.BANG or type == TokenType.MINUS:
            token = self.consume()
            expression = self.parse_unary()
            return Unary(token, expression)
        return self.parse_primary()

    def parse_primary(self):
        token = self.peek()
        match token.type:
            case TokenType.TRUE:
                self.consume()
                return Literal(True)
            case TokenType.FALSE:
                self.consume()
                return Literal(False)
            case TokenType.NIL:
                self.consume()
                return Literal(None)
            case TokenType.NUMBER | TokenType.STRING:
                self.consume()
                return Literal(token.literal)
            case TokenType.LEFT_PAREN:
                self.consume()
                expression = self.parse_expression()
                close = self.peek()
                if close.type != TokenType.RIGHT_PAREN:
                    PloxError.error(close.line, "Unterminated Grouping")
                    raise Exception("Unterminated Grouping")
                else:
                    self.consume()
                    return Grouping(expression)
            case _:
                PloxError.error(token.line, f"Unexpected Token '{token.lexeme}'")
                raise Exception("Unexpected Token")

    def peek(self):
        return self.tokens[self.current]

    def consume(self):
        self.current += 1
        return self.tokens[self.current - 1]

    def is_eof_reached(self):
        return self.tokens[self.current].type == TokenType.EOF

    def synchronize(self):
        while not self.is_eof_reached():
            token = self.peek()
            type = token.type
            match type:
                case TokenType.SEMICOLON:
                    self.consume()
                    return
                case (
                    TokenType.CLASS
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.FOR
                    | TokenType.IF
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ):
                    return
                case _:
                    self.consume()
        self.consume()
