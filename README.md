# Sudoku via SMT (Z3)

    pip install z3-solver
    python sudoku_smt.py hard      # or: easy | empty | <81-char string>

No search loop is written by hand. The 9x9 grid becomes 81 integer variables,
four families of constraints are asserted, and Z3's DPLL(T) engine does the
searching.
