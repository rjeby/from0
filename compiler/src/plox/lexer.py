from src.plox.plox import Plox
from src.plox.token import LiteralValue
from src.plox.token import Token
from src.plox.token import TokenType


class Lexer:
    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, soure: str):
        self.source = soure
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def tokenize(self):
        while not self.is_eof_reached():
            # Set the start of the current token
            self.start = self.current
            self.scan_token()

        self.add_token(TokenType.EOF)
        return self.tokens

    def scan_token(self):
        c = self.consume()
        match (c):
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )

            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )

            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and not self.is_eof_reached():
                        self.consume()
                else:
                    self.add_token(TokenType.SLASH)
            case " ":
                pass
            case "\r":
                pass
            case "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self.scan_string()
            case _:
                if self.is_digit(c):
                    self.scan_number()
                elif self.is_alpha_numeric(c):
                    self.scan_identifier()
                else:
                    Plox.error(self.line, "Unexpected Character")

    def scan_string(self):
        while self.peek() != '"' and not self.is_eof_reached():
            if self.peek() == "\n":
                self.line += 1
            self.consume()
            if self.is_eof_reached():
                Plox.error(self.line, "Unterminated String")
                return
            self.consume()
            self.add_token(
                TokenType.STRING, self.source[self.start + 1 : self.current - 1]
            )

    def scan_number(self):
        while self.is_digit(self.peek()):
            self.consume()
        if self.peek() != "." and self.is_digit(self.peekNext()):
            self.consume()
            while self.is_digit(self.peek()):
                self.consume()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def scan_identifier(self):
        while not self.is_alpha_numeric(self.peek()):
            self.consume()
        text = self.source[self.start : self.current]
        if text in Lexer.keywords:
            self.add_token(Lexer.keywords[text])
        else:
            self.add_token(TokenType.IDENTIFIER)

    def add_token(self, type: TokenType, literal: LiteralValue = None):
        lexeme = self.source[self.start : self.current]
        self.tokens.append(Token(type, lexeme, literal, self.line))

    def consume(self):
        self.current += 1
        return self.source[self.current - 1]

    def peek(self):
        if self.is_eof_reached():
            return "\0"
        return self.source[self.current]

    def peekNext(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def is_eof_reached(self):
        return self.current >= len(self.source)

    def match(self, expected: str):
        if self.is_eof_reached() or self.source[self.current] != expected:
            return False
        self.current = self.current + 1
        return True

    @staticmethod
    def is_digit(c: str):
        return c >= "0" and c <= "9"

    @staticmethod
    def is_alpha(c: str):
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    @staticmethod
    def is_alpha_numeric(c: str):
        return Lexer.is_digit(c) or Lexer.is_alpha(c)
