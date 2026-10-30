"""RoboLang test runner.

Runs every test program through main.py and checks that the output
contains the expected text (and does not contain text that should not
appear). A test passes only if the real output matches.

Usage (from the RoboLang folder, next to main.py):
    python3 run_tests.py

The full output of every run is written to test_log.txt.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

# (id, file, must contain, must NOT contain)
TESTS = [
    ("T1", "programs/phase2_safe.robo",
     ["No semantic errors.", "Variables: {'x': 3, 'steps': 3}",
      "Robot position: (8, 3)", "Direction: SOUTH", "ROBOLANG EXECUTION COMPLETE"],
     ["Error"]),
    ("T2", "programs/phase2_safety_boundary.robo",
     ["may cross the 11x11 grid boundary", "Robot position: (5, 0)", "Direction: NORTH"],
     ["Error"]),
    ("T3", "programs/phase2_semantic_error.robo",
     ["Semantic Error: Variable 'y' is not declared.",
      "Compilation stopped because of semantic errors."],
     ["===== EXECUTION"]),
    ("T4", "programs/phase2_syntax_error.robo",
     ["Syntax Error at line 4: Expected ';' after assignment. (found 'MOVE')"],
     ["===== SEMANTIC"]),
    ("T5", "programs/t_lexical.robo",
     ["Lexical Error at line 2: Unknown character '@'"],
     ["===== ABSTRACT SYNTAX TREE"]),
    ("T6", "programs/t_scope_repeat.robo",
     ["No semantic errors.", "Variables: {'y': 4}", "Robot position: (5, 1)"],
     ["Semantic Error"]),
    ("T7", "programs/t_scope_if.robo",
     ["No semantic errors.", "Variables: {'x': 1, 'z': 3}", "Robot position: (5, 2)"],
     ["Semantic Error"]),
    ("T8", "programs/t_func_leak.robo",
     ["Semantic Error: Variable 'loc' is not declared."],
     ["===== EXECUTION"]),
    ("T9", "programs/t_function.robo",
     ["No semantic errors.", "Function call 'sq' is not expanded",
      "Robot position: (5, 5)", "Direction: WEST"],
     ["Semantic Error"]),
    ("T10", "programs/t_while.robo",
     ["Variables: {'n': 0}", "Robot position: (6, 5)", "Direction: WEST"],
     ["Semantic Error"]),
    ("T11", "programs/t_divzero.robo",
     ["Runtime Error: Division by zero."],
     ["ROBOLANG EXECUTION COMPLETE"]),
]


def main():
    passed = 0
    log = []
    for tid, rel, must, must_not in TESTS:
        path = HERE / rel
        if not path.exists():
            print(f"{tid:<4} {rel:<40} MISSING FILE")
            log.append(f"##### {tid} {rel}\nMISSING FILE\n")
            continue

        run = subprocess.run(
            [sys.executable, "main.py", rel],
            cwd=HERE, capture_output=True, text=True, timeout=30,
        )
        out = run.stdout + run.stderr

        problems = [f"missing: {m!r}" for m in must if m not in out]
        problems += [f"unexpected: {m!r}" for m in must_not if m in out]

        status = "PASS" if not problems else "FAIL"
        passed += status == "PASS"
        print(f"{tid:<4} {rel:<40} {status}")
        for p in problems:
            print(f"       {p}")

        log.append(f"##### {tid} {rel}  ->  {status}\n{out}\n")

    print(f"\n{passed}/{len(TESTS)} tests passed")
    (HERE / "test_log.txt").write_text("\n".join(log), encoding="utf-8")
    print("Full output written to test_log.txt")
    return 0 if passed == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
