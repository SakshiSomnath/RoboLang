"""RoboLang lexical analysis."""

from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    value: str
    line: int


KEYWORDS = {
    "START": "START",
    "END": "END",
    "MOVE": "MOVE",
    "TURN": "TURN",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "REPEAT": "REPEAT",
    "TIMES": "TIMES",
    "IF": "IF",
    "THEN": "THEN",
    "ELSE": "ELSE",
    "WHILE": "WHILE",
    "DO": "DO",
    "DEFINE": "DEFINE",
    "RETURN": "RETURN",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            c = self.source[self.pos]

            if c in " \t\r":
                self.pos += 1
                continue

            if c == "\n":
                self.line += 1
                self.pos += 1
                continue

            # Comments: # comment
            if c == "#":
                while self.pos < len(self.source) and self.source[self.pos] != "\n":
                    self.pos += 1
                continue

            if c.isdigit():
                start = self.pos
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self.pos += 1
                self.tokens.append(Token("NUMBER", self.source[start:self.pos], self.line))
                continue

            if c.isalpha() or c == "_":
                start = self.pos
                while (
                    self.pos < len(self.source)
                    and (self.source[self.pos].isalnum() or self.source[self.pos] == "_")
                ):
                    self.pos += 1
                word = self.source[start:self.pos]
                token_type = KEYWORDS.get(word, "IDENTIFIER")
                self.tokens.append(Token(token_type, word, self.line))
                continue

            two = self.source[self.pos:self.pos + 2]
            if two == "==":
                self.tokens.append(Token("EQUAL_EQUAL", "==", self.line))
                self.pos += 2
                continue
            if two == "!=":
                self.tokens.append(Token("NOT_EQUAL", "!=", self.line))
                self.pos += 2
                continue
            if two == "<=":
                self.tokens.append(Token("LESS_EQUAL", "<=", self.line))
                self.pos += 2
                continue
            if two == ">=":
                self.tokens.append(Token("GREATER_EQUAL", ">=", self.line))
                self.pos += 2
                continue

            single = {
                "=": "ASSIGN",
                "+": "PLUS",
                "-": "MINUS",
                "*": "MULTIPLY",
                "/": "DIVIDE",
                "<": "LESS",
                ">": "GREATER",
                ";": "SEMICOLON",
                "{": "LBRACE",
                "}": "RBRACE",
                "(": "LPAREN",
                ")": "RPAREN",
                ",": "COMMA",
            }

            if c in single:
                self.tokens.append(Token(single[c], c, self.line))
                self.pos += 1
                continue

            raise RuntimeError(
                f"Lexical Error at line {self.line}: Unknown character '{c}'"
            )

        self.tokens.append(Token("EOF", "", self.line))
        return self.tokens


# ============================================================
