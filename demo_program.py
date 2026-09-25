"""Built-in RoboLang demonstration program."""


DEMO_PROGRAM = r"""
START

x = 2 + 1;
steps = x;

REPEAT 2 TIMES {
    MOVE steps;
    TURN RIGHT;
}

IF x > 2 THEN {
    MOVE 1;
} ELSE {
    MOVE 0;
}
END
END
"""


# ============================================================
