"""Robot-specific static analysis for the bounded RoboLang grid."""

from ast_nodes import (
    ASTNode, NumberNode, IdentifierNode, BinaryExpressionNode, AssignmentNode,
    MoveNode, TurnNode, RepeatNode, IfNode, WhileNode, FunctionDefNode,
    FunctionCallNode, ReturnNode, ProgramNode
)

# 6.5 ROBOT PROGRAM ANALYSIS / STATIC SAFETY CHECK
# ============================================================

class RobotProgramAnalyzer:
    """
    Lightweight static analysis for RoboLang's bounded robot grid.

    This stage runs after semantic analysis and before IR generation.
    It tracks statically known robot position/direction and reports
    potential grid-boundary violations before program execution.
    """

    DIRECTIONS = ["NORTH", "EAST", "SOUTH", "WEST"]

    def __init__(self, grid_size=11):
        self.grid_size = grid_size
        self.x = 5
        self.y = 5
        self.direction = 0
        self.constants = {}
        self.warnings = []
        self.checked_moves = 0

    def warn(self, message):
        text = "Robot Analysis Warning: " + message
        if text not in self.warnings:
            self.warnings.append(text)

    def const_eval(self, node):
        """Return an integer if an expression is statically evaluable."""
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, IdentifierNode):
            return self.constants.get(node.name)
        if isinstance(node, BinaryExpressionNode):
            a = self.const_eval(node.left)
            b = self.const_eval(node.right)
            if a is None or b is None:
                return None
            if node.op == "+": return a + b
            if node.op == "-": return a - b
            if node.op == "*": return a * b
            if node.op == "/":
                return None if b == 0 else a // b
            if node.op == "<": return int(a < b)
            if node.op == ">": return int(a > b)
            if node.op == "==": return int(a == b)
            if node.op == "!=": return int(a != b)
            if node.op == "<=": return int(a <= b)
            if node.op == ">=": return int(a >= b)
        return None

    def position_text(self):
        return f"({self.x}, {self.y})"

    def check_move(self, distance):
        if distance < 0:
            self.warn(
                f"MOVE uses a negative distance ({distance}); execution treats it as zero."
            )
            return
        self.checked_moves += 1
        if distance == 0:
            return

        start_x, start_y = self.x, self.y
        dx, dy = 0, 0
        if self.direction == 0:
            dy = -1
        elif self.direction == 1:
            dx = 1
        elif self.direction == 2:
            dy = 1
        else:
            dx = -1

        target_x = start_x + dx * distance
        target_y = start_y + dy * distance

        if not (0 <= target_x < self.grid_size and 0 <= target_y < self.grid_size):
            self.warn(
                f"MOVE {distance} from {self.position_text()} facing "
                f"{self.DIRECTIONS[self.direction]} may cross the "
                f"{self.grid_size}x{self.grid_size} grid boundary."
            )

        # Match the interpreter's current boundary-clamping behaviour.
        self.x = max(0, min(self.grid_size - 1, target_x))
        self.y = max(0, min(self.grid_size - 1, target_y))

    def analyze_statements(self, statements, depth=0):
        if depth > 20:
            self.warn("Analysis depth limit reached while examining nested control flow.")
            return

        for stmt in statements:
            if isinstance(stmt, AssignmentNode):
                value = self.const_eval(stmt.value)
                if value is None:
                    self.constants.pop(stmt.name, None)
                else:
                    self.constants[stmt.name] = value

            elif isinstance(stmt, MoveNode):
                distance = self.const_eval(stmt.distance)
                if distance is None:
                    self.warn(
                        "Could not statically determine a MOVE distance; "
                        "boundary safety cannot be guaranteed for this instruction."
                    )
                else:
                    self.check_move(distance)

            elif isinstance(stmt, TurnNode):
                if stmt.direction == "RIGHT":
                    self.direction = (self.direction + 1) % 4
                else:
                    self.direction = (self.direction - 1) % 4

            elif isinstance(stmt, RepeatNode):
                count = self.const_eval(stmt.count)
                if count is None:
                    self.warn(
                        "Could not statically determine a REPEAT count; "
                        "the loop body was not fully simulated."
                    )
                elif count < 0:
                    self.warn(
                        f"REPEAT uses a negative count ({count}); execution performs zero iterations."
                    )
                elif count > 1000:
                    self.warn("REPEAT count is larger than 1000; static simulation was limited.")
                    for _ in range(1000):
                        self.analyze_statements(stmt.statements, depth + 1)
                else:
                    for _ in range(count):
                        self.analyze_statements(stmt.statements, depth + 1)

            elif isinstance(stmt, IfNode):
                condition = self.const_eval(stmt.condition)
                if condition is not None:
                    if condition != 0:
                        self.analyze_statements(stmt.then_body, depth + 1)
                    else:
                        self.analyze_statements(stmt.else_body, depth + 1)
                else:
                    self.warn(
                        "IF condition is not statically known; both branches may affect robot state."
                    )
                    snapshot = (self.x, self.y, self.direction, dict(self.constants))
                    self.analyze_statements(stmt.then_body, depth + 1)
                    self.x, self.y, self.direction = snapshot[0], snapshot[1], snapshot[2]
                    self.constants = dict(snapshot[3])
                    self.analyze_statements(stmt.else_body, depth + 1)
                    self.x, self.y, self.direction = snapshot[0], snapshot[1], snapshot[2]
                    self.constants = dict(snapshot[3])

            elif isinstance(stmt, WhileNode):
                condition = self.const_eval(stmt.condition)
                if condition == 0:
                    continue
                if condition is not None:
                    self.warn(
                        "WHILE condition is statically true; exact iteration count cannot be proven safe."
                    )
                else:
                    self.warn(
                        "WHILE condition is not statically known; robot state after the loop cannot be determined."
                    )
                snapshot = (self.x, self.y, self.direction, dict(self.constants))
                self.analyze_statements(stmt.body, depth + 1)
                self.x, self.y, self.direction = snapshot[0], snapshot[1], snapshot[2]
                self.constants = dict(snapshot[3])

            elif isinstance(stmt, FunctionDefNode):
                # Function bodies are not expanded here because call paths may
                # depend on runtime arguments/control flow.
                continue

            elif isinstance(stmt, FunctionCallNode):
                self.warn(
                    f"Function call '{stmt.name}' is not expanded during static robot-state analysis."
                )

    def analyze(self, program):
        self.analyze_statements(program.statements)
        return self.warnings


# ============================================================
