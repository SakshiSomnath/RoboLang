"""RoboLang robot interpreter and grid execution engine."""

from ast_nodes import (
    NumberNode, IdentifierNode, BinaryExpressionNode, AssignmentNode, MoveNode,
    TurnNode, RepeatNode, IfNode, WhileNode, FunctionDefNode, FunctionCallNode,
    ReturnNode
)

# 8. ROBOT INTERPRETER
# ============================================================

class ReturnSignal(Exception):
    def __init__(self, value=0):
        self.value = value


class RobotInterpreter:
    # 0 = North, 1 = East, 2 = South, 3 = West
    DIRECTIONS = ["NORTH", "EAST", "SOUTH", "WEST"]

    def __init__(self, functions):
        self.x = 5
        self.y = 5
        self.direction = 0
        self.variables = {}
        self.functions = functions
        self.grid_size = 11
        self.visited = {(self.x, self.y)}

    def truthy(self, value):
        return value != 0

    def eval_expr(self, node, env=None):
        if env is None:
            env = self.variables

        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, IdentifierNode):
            return env.get(node.name, self.variables.get(node.name, 0))

        if isinstance(node, FunctionCallNode):
            args = [self.eval_expr(a, env) for a in node.args]
            return self.call_function(node.name, args)

        if isinstance(node, BinaryExpressionNode):
            a = self.eval_expr(node.left, env)
            b = self.eval_expr(node.right, env)

            if node.op == "+":
                return a + b
            if node.op == "-":
                return a - b
            if node.op == "*":
                return a * b
            if node.op == "/":
                if b == 0:
                    raise RuntimeError("Runtime Error: Division by zero.")
                return a // b
            if node.op == "<":
                return int(a < b)
            if node.op == ">":
                return int(a > b)
            if node.op == "==":
                return int(a == b)
            if node.op == "!=":
                return int(a != b)
            if node.op == "<=":
                return int(a <= b)
            if node.op == ">=":
                return int(a >= b)

        return 0

    def execute(self, statements, env=None):
        if env is None:
            env = self.variables

        for stmt in statements:
            if isinstance(stmt, AssignmentNode):
                env[stmt.name] = self.eval_expr(stmt.value, env)

            elif isinstance(stmt, MoveNode):
                distance = self.eval_expr(stmt.distance, env)
                self.move(distance)

            elif isinstance(stmt, TurnNode):
                if stmt.direction == "RIGHT":
                    self.direction = (self.direction + 1) % 4
                else:
                    self.direction = (self.direction - 1) % 4

            elif isinstance(stmt, RepeatNode):
                count = self.eval_expr(stmt.count, env)
                for _ in range(max(0, count)):
                    self.execute(stmt.statements, env)

            elif isinstance(stmt, IfNode):
                if self.truthy(self.eval_expr(stmt.condition, env)):
                    self.execute(stmt.then_body, env)
                else:
                    self.execute(stmt.else_body, env)

            elif isinstance(stmt, WhileNode):
                safety = 0
                while self.truthy(self.eval_expr(stmt.condition, env)):
                    self.execute(stmt.body, env)
                    safety += 1
                    if safety > 10000:
                        raise RuntimeError(
                            "Runtime Error: WHILE loop exceeded 10000 iterations."
                        )

            elif isinstance(stmt, FunctionCallNode):
                args = [self.eval_expr(a, env) for a in stmt.args]
                self.call_function(stmt.name, args)

            elif isinstance(stmt, ReturnNode):
                value = self.eval_expr(stmt.value, env) if stmt.value else 0
                raise ReturnSignal(value)

            elif isinstance(stmt, FunctionDefNode):
                # Definitions are collected before execution.
                pass

    def call_function(self, name, args):
        if name not in self.functions:
            raise RuntimeError(f"Runtime Error: Function '{name}' not found.")

        function = self.functions[name]

        if len(args) != len(function.params):
            raise RuntimeError(
                f"Runtime Error: Function '{name}' expects "
                f"{len(function.params)} arguments but got {len(args)}."
            )

        local_env = dict(zip(function.params, args))

        try:
            self.execute(function.body, local_env)
        except ReturnSignal as r:
            return r.value

        return 0

    def move(self, distance):
        for _ in range(max(0, distance)):
            if self.direction == 0:
                self.y -= 1
            elif self.direction == 1:
                self.x += 1
            elif self.direction == 2:
                self.y += 1
            else:
                self.x -= 1

            self.x = max(0, min(self.grid_size - 1, self.x))
            self.y = max(0, min(self.grid_size - 1, self.y))
            self.visited.add((self.x, self.y))

    def show_grid(self):
        print("\n===== ROBOT GRID =====")
        for row in range(self.grid_size):
            line = ""
            for col in range(self.grid_size):
                if col == self.x and row == self.y:
                    line += "R "
                elif (col, row) in self.visited:
                    line += ". "
                else:
                    line += "- "
            print(line)

        print(
            f"\nRobot position: ({self.x}, {self.y})"
            f"\nDirection: {self.DIRECTIONS[self.direction]}"
        )
        print("R = Robot, . = Visited path")


# ============================================================
