from src.plox.statement import Statement
from src.plox.statement import FuncDeclarationStatement
from src.plox.statement import WhileStatement
from src.plox.statement import IfStatement
from src.plox.statement import BlockStatement
from src.plox.statement import ExpressionStatement
from src.plox.statement import VarDeclarationStatement
from src.plox.statement import PrintStatement
from src.plox.expression import CallExpression
from src.plox.expression import Variable
from src.plox.expression import Assignment
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

    def parse(self):
        statements: list[Statement] = []
        while not self.is_eof_reached():
            statement = self.parse_declaration()
            statements.append(statement)

        return statements

    def parse_declaration(self) -> Statement:
        token = self.peek()
        if token.type == TokenType.FUN:
            return self.parse_function()
        if token.type == TokenType.VAR:
            return self.parse_variable_declaration()

        return self.parse_statement()

    def parse_function(self):
        token = self.peek()
        if token.type != TokenType.IDENTIFIER:
            PloxError.error(token.line, "Expected an Identifier")
            raise Exception("Expected an Identifier")
        name = self.consume()
        token = self.peek()
        if token.type != TokenType.LEFT_PAREN:
            PloxError.error(token.line, "Expected an Opening Parenthesis")
            raise Exception("Expected an Opening Parenthesis")
        self.consume()
        params = self.parse_parameters()
        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            PloxError.error(token.line, "Expected an Closing Parenthesis")
            raise Exception("Expected an Closing Parenthesis")
        body = self.parse_block_statement()
        return FuncDeclarationStatement(name, params, body)

    def parse_parameters(self):
        params: list[Token] = []
        token = self.peek()
        if token.type == TokenType.RIGHT_PAREN:
            self.consume()
            return params
        self.consume()
        token = self.peek()
        if token.type != TokenType.IDENTIFIER:
            PloxError.error(token.line, "Expected an Identifier")
            raise Exception("Expected an Identifier")
        params.append(token)
        while self.peek().type == TokenType.COMMA:
            self.consume()
            token = self.peek()
            if token.type != TokenType.IDENTIFIER:
                PloxError.error(token.line, "Expected an Identifier")
                raise Exception("Expected an Identifier")
            self.consume()
            params.append(token)
            if len(params) >= 255:
                PloxError.error(token.line, "Max Paramaters Count Exceeded")
                raise Exception("Max Parameters Count Exceeded")

        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            PloxError.error(token.line, "Expected a Closing Parenthesis")
            raise Exception("Expected a Closing Parenthesis")
        self.consume()
        return params

    def parse_statement(self) -> Statement:
        token = self.peek()
        if token.type == TokenType.PRINT:
            return self.parse_print_statement()
        if token.type == TokenType.LEFT_BRACE:
            return self.parse_block_statement()
        if token.type == TokenType.IF:
            return self.parse_if_statement()
        if token.type == TokenType.WHILE:
            return self.parse_while_statement()
        if token.type == TokenType.FOR:
            return self.parse_for_statement()
        return self.parse_expression_statement()

    def parse_for_statement(self):
        self.consume()
        token = self.peek()
        if token.type != TokenType.LEFT_PAREN:
            PloxError.error(token.line, "Expected an Opening Parenthesis")
            raise Exception("Expected an Opening Parenthesis")
        self.consume()
        initializer = None
        token = self.peek()
        if token.type == TokenType.SEMICOLON:
            self.consume()
        elif token.type == TokenType.VAR:
            initializer = self.parse_variable_declaration()
        else:
            initializer = self.parse_expression_statement()
        condition = None
        token = self.peek()
        if token.type != TokenType.SEMICOLON:
            condition = self.parse_expression()
        token = self.peek()
        if token.type != TokenType.SEMICOLON:
            PloxError.error(token.line, "Expected a Semicolon")
            raise Exception("Expected a Semicolon")
        self.consume()
        increment = None
        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            increment = self.parse_expression()
        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            PloxError.error(token.line, "Expected a Closing Parenthesis")
            raise Exception("Expected a closing Parenthesis")
        self.consume()
        body = self.parse_statement()
        if increment != None:
            body = BlockStatement([body, ExpressionStatement(increment)])
        if condition == None:
            condition = Literal(True)
        body = WhileStatement(condition, body)
        if initializer != None:
            body = BlockStatement([initializer, body])
        return body

    def parse_while_statement(self):
        self.consume()
        token = self.peek()
        if token.type != TokenType.LEFT_PAREN:
            PloxError.error(token.line, "Expected an Opening Parenthesis")
            raise Exception("Expected an Opening Parenthesis")
        self.consume()
        condition = self.parse_expression()
        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            PloxError.error(token.line, "Expected a Closing Parenthesis")
            raise Exception("Expected a Closing Parenthesis")
        self.consume()
        body = self.parse_statement()
        return WhileStatement(condition, body)

    def parse_if_statement(self):
        self.consume()
        token = self.peek()
        if token.type != TokenType.LEFT_PAREN:
            PloxError.error(token.line, "Expected an Opening Parenthesis")
            raise Exception("Expected an Opening Parenthesis")
        self.consume()
        condition = self.parse_expression()
        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            PloxError.error(token.line, "Expected a Closing Parenthesis")
            raise Exception("Expected a Closing Parenthesis")
        self.consume()
        then_branch = self.parse_statement()
        else_branch = None
        token = self.peek()
        if token.type == TokenType.ELSE:
            self.consume()
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch)

    def parse_block_statement(self):
        statements: list[Statement] = []
        self.consume()
        while self.peek().type != TokenType.RIGHT_BRACE and not self.is_eof_reached():
            declaration = self.parse_declaration()
            statements.append(declaration)
        token = self.peek()
        if token.type != TokenType.RIGHT_BRACE:
            PloxError.error(token.line, "Unterminated Block")
            raise Exception("Unterminated Block")
        self.consume()
        return BlockStatement(statements)

    def parse_variable_declaration(self):
        self.consume()
        token = self.peek()
        if token.type != TokenType.IDENTIFIER:
            PloxError.error(token.line, "Expected an Identifier")
            raise Exception("Expected an Identifier")
        identifier = self.consume()
        initializer = None
        if self.peek().type == TokenType.EQUAL:
            self.consume()
            initializer = self.parse_expression()
        if token.type != TokenType.IDENTIFIER:
            PloxError.error(token.line, "Expected a Semicolon")
            raise Exception("Expected a Semicolon")
        self.consume()
        return VarDeclarationStatement(identifier, initializer)

    def parse_print_statement(self):
        self.consume()
        expression = self.parse_expression()
        token = self.peek()
        if token.type != TokenType.SEMICOLON:
            PloxError.error(token.line, "Expected a Semicolon")
            raise Exception("Expected a Semicolon")
        self.consume()
        return PrintStatement(expression)

    def parse_expression_statement(self):
        expression = self.parse_expression()
        token = self.peek()
        if token.type != TokenType.SEMICOLON:
            PloxError.error(token.line, "Expected a Semicolon")
            raise Exception("Expected a Semicolon")
        self.consume()
        return ExpressionStatement(expression)

    def parse_expression(self) -> Expression:
        return self.parse_assignment()

    def parse_assignment(self) -> Expression:
        expression = self.parse_logic_or()
        token = self.peek()
        if token.type == TokenType.EQUAL:
            if isinstance(expression, Variable):
                self.consume()
                name = expression.name
                value = self.parse_assignment()
                return Assignment(name, value)
            PloxError.error(token.line, "Invalid Assignment Target")
            # TODO: No need for synchronization
            raise Exception("Invalid Assignment Target")
        return expression

    def parse_logic_or(self):
        expression = self.parse_logic_and()
        while self.peek().type == TokenType.OR:
            token = self.consume()
            right = self.parse_logic_and()
            expression = Binary(expression, token, right)
        return expression

    def parse_logic_and(self):
        expression = self.parse_equality()
        while self.peek().type == TokenType.AND:
            token = self.consume()
            right = self.parse_equality()
            expression = Binary(expression, token, right)
        return expression

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
        return self.parse_call()

    def parse_call(self):
        expression = self.parse_primary()
        token = self.peek()

        while self.peek().type == TokenType.LEFT_PAREN:
            token = self.consume()
            arguments = self.parse_arguments()
            expression = CallExpression(expression, token, arguments)
        return expression

    def parse_arguments(self):
        arguments: list[Expression] = []
        token = self.peek()
        if token.type == TokenType.RIGHT_PAREN:
            self.consume()
            return arguments
        self.consume()
        expression = self.parse_expression()
        arguments.append(expression)
        while self.peek().type == TokenType.COMMA:
            self.consume()
            expression = self.parse_expression()
            arguments.append(expression)
            if len(arguments) >= 255:
                PloxError.error(token.line, "Max Arguments Count Exceeded")
                raise Exception("Max Arguments Count Exceeded")

        token = self.peek()
        if token.type != TokenType.RIGHT_PAREN:
            PloxError.error(token.line, "Expected a Closing Parenthesis")
            raise Exception("Expected a Closing Parenthesis")
        self.consume()
        return arguments

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
            case TokenType.IDENTIFIER:
                self.consume()
                return Variable(token)
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
