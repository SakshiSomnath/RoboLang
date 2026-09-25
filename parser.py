"""RoboLang recursive-descent parser."""

from typing import List

from lexer import Token
from ast_nodes import (
    ASTNode, NumberNode, IdentifierNode, BinaryExpressionNode, AssignmentNode,
    MoveNode, TurnNode, RepeatNode, IfNode, WhileNode, FunctionDefNode,
    FunctionCallNode, ReturnNode, ProgramNode
)

# 3. RECURSIVE-DESCENT PARSER
# ============================================================

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        token = self.peek()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token

    def check(self, token_type: str) -> bool:
        return self.peek().type == token_type

    def match(self, *types: str) -> bool:
        if self.peek().type in types:
            self.advance()
            return True
        return False

    def consume(self, token_type: str, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise RuntimeError(
            f"Syntax Error at line {self.peek().line}: {message} "
            f"(found '{self.peek().value}')"
        )

    def parse(self) -> ProgramNode:
        self.consume("START", "Program must begin with START.")

        statements = []
        while not self.check("END") and not self.check("EOF"):
            statements.append(self.parse_statement())

        self.consume("END", "Program must end with END.")
        return ProgramNode(statements)

    def parse_statement(self) -> ASTNode:
        if self.match("MOVE"):
            distance = self.expression()
            self.consume("SEMICOLON", "Expected ';' after MOVE.")
            return MoveNode(distance)

        if self.match("TURN"):
            if self.match("LEFT"):
                direction = "LEFT"
            elif self.match("RIGHT"):
                direction = "RIGHT"
            else:
                raise RuntimeError(
                    f"Syntax Error at line {self.peek().line}: "
                    "Expected LEFT or RIGHT after TURN."
                )
            self.consume("SEMICOLON", "Expected ';' after TURN.")
            return TurnNode(direction)

        if self.match("REPEAT"):
            count = self.expression()
            self.consume("TIMES", "Expected TIMES after REPEAT expression.")
            body = self.parse_braced_block()
            return RepeatNode(count, body)

        if self.match("IF"):
            condition = self.expression()
            self.consume("THEN", "Expected THEN after IF condition.")
            then_body = self.parse_braced_block()

            else_body = []
            if self.match("ELSE"):
                else_body = self.parse_braced_block()

            self.consume("END", "Expected END after IF statement.")
            return IfNode(condition, then_body, else_body)

        if self.match("WHILE"):
            condition = self.expression()
            self.consume("DO", "Expected DO after WHILE condition.")
            body = self.parse_braced_block()
            self.consume("END", "Expected END after WHILE statement.")
            return WhileNode(condition, body)

        if self.match("DEFINE"):
            name = self.consume("IDENTIFIER", "Expected function name.").value
            self.consume("LPAREN", "Expected '(' after function name.")

            params = []
            if not self.check("RPAREN"):
                params.append(self.consume("IDENTIFIER", "Expected parameter name.").value)
                while self.match("COMMA"):
                    params.append(
                        self.consume("IDENTIFIER", "Expected parameter name.").value
                    )

            self.consume("RPAREN", "Expected ')' after parameters.")
            body = self.parse_braced_block()
            self.consume("END", "Expected END after function definition.")
            return FunctionDefNode(name, params, body)

        if self.match("RETURN"):
            if self.check("SEMICOLON"):
                self.advance()
                return ReturnNode(None)
            value = self.expression()
            self.consume("SEMICOLON", "Expected ';' after RETURN.")
            return ReturnNode(value)

        if self.check("IDENTIFIER"):
            name = self.advance().value

            # Function call
            if self.match("LPAREN"):
                args = []
                if not self.check("RPAREN"):
                    args.append(self.expression())
                    while self.match("COMMA"):
                        args.append(self.expression())
                self.consume("RPAREN", "Expected ')' after function arguments.")
                self.consume("SEMICOLON", "Expected ';' after function call.")
                return FunctionCallNode(name, args)

            # Assignment
            self.consume("ASSIGN", "Expected '=' after identifier.")
            value = self.expression()
            self.consume("SEMICOLON", "Expected ';' after assignment.")
            return AssignmentNode(name, value)

        raise RuntimeError(
            f"Syntax Error at line {self.peek().line}: "
            f"Unexpected token '{self.peek().value}'."
        )

    def parse_braced_block(self) -> List[ASTNode]:
        self.consume("LBRACE", "Expected '{' to start block.")
        statements = []

        while not self.check("RBRACE") and not self.check("EOF"):
            statements.append(self.parse_statement())

        self.consume("RBRACE", "Expected '}' after block.")
        return statements

    # expression -> comparison
    def expression(self) -> ASTNode:
        return self.comparison()

    def comparison(self) -> ASTNode:
        node = self.term()

        while self.match(
            "LESS",
            "GREATER",
            "EQUAL_EQUAL",
            "NOT_EQUAL",
            "LESS_EQUAL",
            "GREATER_EQUAL",
        ):
            op = self.previous().value
            right = self.term()
            node = BinaryExpressionNode(node, op, right)

        return node

    def term(self) -> ASTNode:
        node = self.factor()

        while self.match("PLUS", "MINUS"):
            op = self.previous().value
            right = self.factor()
            node = BinaryExpressionNode(node, op, right)

        return node

    def factor(self) -> ASTNode:
        node = self.unary()

        while self.match("MULTIPLY", "DIVIDE"):
            op = self.previous().value
            right = self.unary()
            node = BinaryExpressionNode(node, op, right)

        return node

    def unary(self) -> ASTNode:
        if self.match("MINUS"):
            return BinaryExpressionNode(NumberNode(0), "-", self.unary())

        return self.primary()

    def primary(self) -> ASTNode:
        if self.match("NUMBER"):
            return NumberNode(int(self.previous().value))

        if self.match("IDENTIFIER"):
            name = self.previous().value

            # Function call inside expression
            if self.match("LPAREN"):
                args = []
                if not self.check("RPAREN"):
                    args.append(self.expression())
                    while self.match("COMMA"):
                        args.append(self.expression())
                self.consume("RPAREN", "Expected ')' after function arguments.")
                return FunctionCallNode(name, args)

            return IdentifierNode(name)

        if self.match("LPAREN"):
            node = self.expression()
            self.consume("RPAREN", "Expected ')' after expression.")
            return node

        raise RuntimeError(
            f"Syntax Error at line {self.peek().line}: "
            "Expected number, identifier, or '(' expression ')'."
        )


# ============================================================
