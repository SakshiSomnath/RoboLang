"""RoboLang intermediate-code optimization."""

from typing import List

# 7. OPTIMIZATION - CONSTANT FOLDING
# ============================================================

def optimize_ir(ir: List[str]) -> List[str]:
    optimized = []

    for line in ir:
        parts = line.split()

        # Example: t1 = 2 + 3
        if len(parts) == 5 and parts[1] == "=":
            left = parts[2]
            op = parts[3]
            right = parts[4]

            if left.lstrip("-").isdigit() and right.lstrip("-").isdigit():
                a = int(left)
                b = int(right)

                if op == "+":
                    result = a + b
                elif op == "-":
                    result = a - b
                elif op == "*":
                    result = a * b
                elif op == "/" and b != 0:
                    result = a // b
                else:
                    optimized.append(line)
                    continue

                optimized.append(f"{parts[0]} = {result}")
                continue

        optimized.append(line)

    return optimized


# ============================================================
