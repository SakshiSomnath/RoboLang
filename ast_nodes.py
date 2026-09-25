"""RoboLang Abstract Syntax Tree node definitions and printer."""

from dataclasses import dataclass
from typing import List, Optional

# 2. AST NODES
# ============================================================

class ASTNode:
    pass


@dataclass
class NumberNode(ASTNode):
    value: int


@dataclass
class IdentifierNode(ASTNode):
    name: str


@dataclass
class BinaryExpressionNode(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode


@dataclass
class AssignmentNode(ASTNode):
    name: str
    value: ASTNode


@dataclass
class MoveNode(ASTNode):
    distance: ASTNode


@dataclass
class TurnNode(ASTNode):
    direction: str


@dataclass
class RepeatNode(ASTNode):
    count: ASTNode
    statements: List[ASTNode]


@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: List[ASTNode]


@dataclass
class WhileNode(ASTNode):
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class FunctionDefNode(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]


@dataclass
class FunctionCallNode(ASTNode):
    name: str
    args: List[ASTNode]


@dataclass
class ReturnNode(ASTNode):
    value: Optional[ASTNode]


@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]


# ============================================================


# 4. AST PRINTER
# ============================================================

def print_ast(node: ASTNode, level: int = 0) -> None:
    indent = "  " * level

    if isinstance(node, ProgramNode):
        print(indent + "PROGRAM")
        for stmt in node.statements:
            print_ast(stmt, level + 1)

    elif isinstance(node, NumberNode):
        print(indent + f"NUMBER: {node.value}")

    elif isinstance(node, IdentifierNode):
        print(indent + f"IDENTIFIER: {node.name}")

    elif isinstance(node, BinaryExpressionNode):
        print(indent + f"OPERATOR: {node.op}")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)

    elif isinstance(node, AssignmentNode):
        print(indent + f"ASSIGNMENT: {node.name}")
        print_ast(node.value, level + 1)

    elif isinstance(node, MoveNode):
        print(indent + "MOVE")
        print_ast(node.distance, level + 1)

    elif isinstance(node, TurnNode):
        print(indent + f"TURN: {node.direction}")

    elif isinstance(node, RepeatNode):
        print(indent + "REPEAT")
        print_ast(node.count, level + 1)
        for stmt in node.statements:
            print_ast(stmt, level + 1)

    elif isinstance(node, IfNode):
        print(indent + "IF")
        print(indent + "  CONDITION")
        print_ast(node.condition, level + 2)
        print(indent + "  THEN")
        for stmt in node.then_body:
            print_ast(stmt, level + 2)
        if node.else_body:
            print(indent + "  ELSE")
            for stmt in node.else_body:
                print_ast(stmt, level + 2)

    elif isinstance(node, WhileNode):
        print(indent + "WHILE")
        print_ast(node.condition, level + 1)
        for stmt in node.body:
            print_ast(stmt, level + 1)

    elif isinstance(node, FunctionDefNode):
        print(indent + f"FUNCTION: {node.name}({', '.join(node.params)})")
        for stmt in node.body:
            print_ast(stmt, level + 1)

    elif isinstance(node, FunctionCallNode):
        print(indent + f"CALL: {node.name}")
        for arg in node.args:
            print_ast(arg, level + 1)

    elif isinstance(node, ReturnNode):
        print(indent + "RETURN")
        if node.value:
            print_ast(node.value, level + 1)


# ============================================================
