"""RoboLang compiler driver.

Pipeline:
Source -> Lexer -> Parser/AST -> Semantic Analysis/Symbol Table
       -> Robot Program Analysis -> Three Address Code (IR)
       -> Constant Folding Optimization -> Interpreter -> Robot Grid

Run:
    python3 main.py
    python3 main.py program.robo
"""

import sys

from lexer import Lexer
from parser import Parser
from ast_nodes import print_ast
from semantic import SemanticAnalyzer
from robot_analysis import RobotProgramAnalyzer
from ir import IRGenerator
from optimizer import optimize_ir
from interpreter import RobotInterpreter
from utils import print_tokens, print_ir, collect_functions
from demo_program import DEMO_PROGRAM



def main():
    print("========================================")
    print("          ROBOLANG COMPILER")
    print("========================================")
    print("Lexer -> Parser -> AST -> Semantic Analysis")
    print("      -> Robot Program Analysis -> IR")
    print("      -> Optimization -> Interpreter")
    print("========================================\n")

    # Read .robo file if supplied, otherwise use demo.
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, "r", encoding="utf-8") as f:
                source = f.read()
        except OSError as e:
            print(f"File Error: {e}")
            return
    else:
        source = DEMO_PROGRAM

    print("===== SOURCE PROGRAM =====")
    print(source.strip())
    print()

    # ---------------- LEXER ----------------
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        print_tokens(tokens)
    except RuntimeError as e:
        print(e)
        return

    # ---------------- PARSER ----------------
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except RuntimeError as e:
        print(e)
        return

    print("===== ABSTRACT SYNTAX TREE =====")
    print_ast(ast)
    print()

    # ---------------- SEMANTIC ANALYSIS ----------------
    semantic = SemanticAnalyzer()
    errors = semantic.analyze(ast)

    print("===== SEMANTIC ANALYSIS =====")
    if errors:
        for error in errors:
            print(error)
        print("\nCompilation stopped because of semantic errors.")
        return
    else:
        print("No semantic errors.")
        print("Symbol table check: PASSED")
    print()

    # ---------------- ROBOT PROGRAM ANALYSIS ----------------
    robot_analyzer = RobotProgramAnalyzer(grid_size=11)
    robot_warnings = robot_analyzer.analyze(ast)

    print("===== ROBOT PROGRAM ANALYSIS =====")
    if robot_warnings:
        for warning in robot_warnings:
            print(warning)
        print(f"Static analysis completed with {len(robot_warnings)} warning(s).")
    else:
        print("No statically detectable robot-state safety issues.")
    print(
        f"Predicted robot state: position {robot_analyzer.position_text()}, "
        f"direction {robot_analyzer.DIRECTIONS[robot_analyzer.direction]}"
    )
    print()

    # ---------------- IR GENERATION ----------------
    ir_generator = IRGenerator()
    ir = ir_generator.generate(ast)

    print_ir("===== THREE ADDRESS CODE (IR) =====", ir)

    # ---------------- OPTIMIZATION ----------------
    optimized_ir = optimize_ir(ir)

    print_ir("===== OPTIMIZED IR =====", optimized_ir)

    print(
        f"Optimization: {len(ir)} instructions -> "
        f"{len(optimized_ir)} instructions"
    )
    print()

    # ---------------- INTERPRETER ----------------
    functions = collect_functions(ast)
    interpreter = RobotInterpreter(functions)

    try:
        interpreter.execute(ast.statements)
    except RuntimeError as e:
        print(e)
        return

    print("===== EXECUTION =====")
    print("Program executed successfully.")
    print(f"Variables: {interpreter.variables}")
    interpreter.show_grid()

    print("\n========================================")
    print("       ROBOLANG EXECUTION COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
