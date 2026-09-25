RoboLang - Modular Phase 2 Project

Run from this folder:
  python3 main.py
  python3 main.py programs/phase2_safe.robo
  python3 main.py programs/phase2_safety_boundary.robo
  python3 main.py programs/phase2_semantic_error.robo
  python3 main.py programs/phase2_syntax_error.robo

Modules:
  lexer.py           Lexical analysis / tokens
  ast_nodes.py       AST node definitions + AST printer
  parser.py          Recursive-descent syntax analysis
  semantic.py        Semantic analysis + symbol tables
  robot_analysis.py  Robot-specific static safety analysis (new Phase 2 feature)
  ir.py              Three-address-style intermediate code
  optimizer.py       Constant-folding optimization
  interpreter.py     Robot execution + grid visualization
  utils.py           Output helpers and function collection
  demo_program.py    Built-in demo source
  main.py            Compiler pipeline / driver only
