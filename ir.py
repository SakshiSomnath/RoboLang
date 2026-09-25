"""Three-address-style intermediate representation generation."""

from ast_nodes import (
    ASTNode, NumberNode, IdentifierNode, BinaryExpressionNode, AssignmentNode,
    MoveNode, TurnNode, RepeatNode, IfNode, WhileNode, FunctionDefNode,
    FunctionCallNode, ReturnNode, ProgramNode
)

# 6. THREE-ADDRESS CODE / INTERMEDIATE REPRESENTATION
# ============================================================

class IRGenerator:
    def __init__(self):
        self.code: List[str] = []
        self.temp = 0
        self.label = 0

    def new_temp(self):
        self.temp += 1
        return f"t{self.temp}"

    def new_label(self):
        self.label += 1
        return f"L{self.label}"

    def emit(self, text):
        self.code.append(text)

    def generate(self, program: ProgramNode):
        for stmt in program.statements:
            self.gen_statement(stmt)
        return self.code

    def gen_statement(self, node):
        if isinstance(node, AssignmentNode):
            value = self.gen_expr(node.value)
            self.emit(f"{node.name} = {value}")

        elif isinstance(node, MoveNode):
            value = self.gen_expr(node.distance)
            self.emit(f"MOVE {value}")

        elif isinstance(node, TurnNode):
            self.emit(f"TURN {node.direction}")

        elif isinstance(node, RepeatNode):
            count = self.gen_expr(node.count)
            start = self.new_label()
            end = self.new_label()
            temp = self.new_temp()
            self.emit(f"{temp} = {count}")
            self.emit(f"LABEL {start}")
            self.emit(f"IF {temp} <= 0 GOTO {end}")
            for stmt in node.statements:
                self.gen_statement(stmt)
            self.emit(f"{temp} = {temp} - 1")
            self.emit(f"GOTO {start}")
            self.emit(f"LABEL {end}")

        elif isinstance(node, IfNode):
            cond = self.gen_expr(node.condition)
            else_label = self.new_label()
            end_label = self.new_label()

            self.emit(f"IF_FALSE {cond} GOTO {else_label}")
            for stmt in node.then_body:
                self.gen_statement(stmt)
            self.emit(f"GOTO {end_label}")
            self.emit(f"LABEL {else_label}")
            for stmt in node.else_body:
                self.gen_statement(stmt)
            self.emit(f"LABEL {end_label}")

        elif isinstance(node, WhileNode):
            start = self.new_label()
            end = self.new_label()
            self.emit(f"LABEL {start}")
            cond = self.gen_expr(node.condition)
            self.emit(f"IF_FALSE {cond} GOTO {end}")
            for stmt in node.body:
                self.gen_statement(stmt)
            self.emit(f"GOTO {start}")
            self.emit(f"LABEL {end}")

        elif isinstance(node, FunctionDefNode):
            self.emit(f"FUNCTION {node.name}")
            for stmt in node.body:
                self.gen_statement(stmt)
            self.emit("END_FUNCTION")

        elif isinstance(node, FunctionCallNode):
            args = [self.gen_expr(a) for a in node.args]
            self.emit(f"CALL {node.name}({', '.join(args)})")

        elif isinstance(node, ReturnNode):
            if node.value:
                self.emit(f"RETURN {self.gen_expr(node.value)}")
            else:
                self.emit("RETURN")

    def gen_expr(self, node):
        if isinstance(node, NumberNode):
            return str(node.value)

        if isinstance(node, IdentifierNode):
            return node.name

        if isinstance(node, FunctionCallNode):
            args = [self.gen_expr(a) for a in node.args]
            temp = self.new_temp()
            self.emit(f"{temp} = CALL {node.name}({', '.join(args)})")
            return temp

        if isinstance(node, BinaryExpressionNode):
            left = self.gen_expr(node.left)
            right = self.gen_expr(node.right)
            temp = self.new_temp()
            self.emit(f"{temp} = {left} {node.op} {right}")
            return temp

        return "0"


# ============================================================
