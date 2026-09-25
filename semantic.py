"""RoboLang semantic analysis and symbol-table management."""

from ast_nodes import (
    ASTNode, NumberNode, IdentifierNode, BinaryExpressionNode, AssignmentNode,
    MoveNode, TurnNode, RepeatNode, IfNode, WhileNode, FunctionDefNode,
    FunctionCallNode, ReturnNode, ProgramNode
)

# 5. SEMANTIC ANALYSIS + SYMBOL TABLE
# ============================================================

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]
        self.functions = {}
        self.errors = []

    def error(self, message: str):
        self.errors.append("Semantic Error: " + message)

    def declare(self, name: str):
        self.scopes[-1][name] = True

    def is_declared(self, name: str) -> bool:
        return any(name in scope for scope in reversed(self.scopes))

    def analyze(self, program: ProgramNode):
        # First collect function definitions.
        for stmt in program.statements:
            if isinstance(stmt, FunctionDefNode):
                if stmt.name in self.functions:
                    self.error(f"Function '{stmt.name}' is already defined.")
                else:
                    self.functions[stmt.name] = stmt

        for stmt in program.statements:
            self.visit(stmt)

        return self.errors

    def visit(self, node: ASTNode):
        if isinstance(node, ProgramNode):
            for s in node.statements:
                self.visit(s)

        elif isinstance(node, AssignmentNode):
            self.visit(node.value)
            self.declare(node.name)

        elif isinstance(node, IdentifierNode):
            if not self.is_declared(node.name):
                self.error(f"Variable '{node.name}' is not declared.")

        elif isinstance(node, BinaryExpressionNode):
            self.visit(node.left)
            self.visit(node.right)

        elif isinstance(node, MoveNode):
            self.visit(node.distance)

        # REPEAT does NOT create a new scope.
        elif isinstance(node, RepeatNode):
            self.visit(node.count)

            for s in node.statements:
                self.visit(s)

        # IF does NOT create a new scope.
        elif isinstance(node, IfNode):
            self.visit(node.condition)

            for s in node.then_body:
                self.visit(s)

            if node.else_body:
                for s in node.else_body:
                    self.visit(s)

        # WHILE does NOT create a new scope.
        elif isinstance(node, WhileNode):
            self.visit(node.condition)

            for s in node.body:
                self.visit(s)

        # Functions DO create a separate scope.
        elif isinstance(node, FunctionDefNode):
            self.scopes.append({})

            for p in node.params:
                self.declare(p)

            for s in node.body:
                self.visit(s)

            self.scopes.pop()

        elif isinstance(node, FunctionCallNode):
            if node.name not in self.functions:
                self.error(f"Function '{node.name}' is not defined.")

            for arg in node.args:
                self.visit(arg)

        elif isinstance(node, ReturnNode):
            if node.value:
                self.visit(node.value)


# ============================================================