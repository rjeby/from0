from src.plox.expression import Literal
from src.plox.expression import Expression
from src.plox.expression import Binary
from src.plox.expression import Unary
from src.plox.expression import Grouping
from src.plox.token import Token
from src.plox.token import TokenType
from src.plox.plox import Plox


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse_expression(self) -> Expression:
        return self.parse_equality()

    def parse_equality(self):
        expression = self.parse_comparison()
        while (
            self.peek() == TokenType.BANG_EQUAL or self.peek() == TokenType.EQUAL_EQUAL
        ):
            token = self.consume()
            right = self.parse_comparison()
            expression = Binary(expression, token, right)
        return expression

    def parse_comparison(self):
        expression = self.parse_term()
        while (
            self.peek() == TokenType.GREATER
            or self.peek() == TokenType.GREATER_EQUAL
            or self.peek() == TokenType.LESS
            or self.peek() == TokenType.LESS_EQUAL
        ):
            token = self.consume()
            right = self.parse_term()
            expression = Binary(expression, token, right)
        return expression

    def parse_term(self):
        expression = self.parse_factor()
        while self.peek() == TokenType.MINUS or self.peek() == TokenType.PLUS:
            token = self.consume()
            right = self.parse_factor()
            expression = Binary(expression, token, right)
        return expression

    def parse_factor(self):
        expression = self.parse_unary()
        while self.peek() == TokenType.SLASH or self.peek() == TokenType.STAR:
            token = self.consume()
            right = self.parse_unary()
            expression = Binary(expression, token, right)
        return expression

    def parse_unary(self) -> Expression:
        type = self.peek()
        match type:
            case TokenType.BANG | TokenType.MINUS:
                token = self.consume()
                expression = self.parse_unary()
                return Unary(token, expression)
            case (
                TokenType.NUMBER
                | TokenType.STRING
                | TokenType.TRUE
                | TokenType.FALSE
                | TokenType.NIL
                | TokenType.SLASH
            ):
                return self.parse_primary()
            case _:
                Plox.error(-1, "Unexpected Token")
                raise Exception("Unexpected Token")

    def parse_primary(self):
        token = self.consume()
        match token.type:
            case TokenType.TRUE:
                return Literal(True)
            case TokenType.FALSE:
                return Literal(False)
            case TokenType.NIL:
                return Literal(None)
            case TokenType.NUMBER | TokenType.STRING:
                return Literal(token.literal)
            case TokenType.SLASH:
                expression = self.parse_expression()
                if self.peek() != TokenType.SLASH:
                    Plox.error(token.line, "Unterminated Grouping")
                    raise Exception("Unterminated Grouping")
                else:
                    self.consume()
                    return Grouping(expression)

            case _:
                Plox.error(token.line, "Unexpected Token")
                raise Exception("Unexpected Token")

    def peek(self):
        if self.current >= len(self.tokens):
            return TokenType.EOF
        return self.tokens[self.current].type

    def consume(self):
        self.current += 1
        return self.tokens[self.current]

    def is_eof_reached(self):
        return self.current >= len(self.tokens)
