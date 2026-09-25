"""RoboLang display and AST helper functions."""

from ast_nodes import ASTNode, FunctionDefNode

# 9. HELPERS
# ============================================================

def print_tokens(tokens):
    print("===== TOKENS =====")
    for token in tokens:
        if token.type != "EOF":
            print(f"{token.type:<15} {token.value}")
    print()


def print_ir(title, ir):
    print(title)
    for i, line in enumerate(ir, 1):
        print(f"{i:02}: {line}")
    print()


def collect_functions(program):
    return {
        stmt.name: stmt
        for stmt in program.statements
        if isinstance(stmt, FunctionDefNode)
    }


# ============================================================
