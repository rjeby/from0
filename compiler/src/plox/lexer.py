from src.plox.token import Token
from src.plox.token import TokenType


class Lexer:
    def __init__(self, soure: str):
        self.source = soure
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def tokenize(self):
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
            case "/":
                self.add_token(TokenType.SLASH)
            case "*":
                self.add_token(TokenType.STAR)
            case _:
                raise Exception("Unexpected Token")

    def add_token(self, type: TokenType):
        lexeme = self.source[self.start : self.current]
        self.tokens.append(Token(type, lexeme, self.line))

    def consume(self):
        self.current += 1
        return self.source[self.current - 1]

    def is_eof_Reached(self):
        return self.current >= len(self.source)
