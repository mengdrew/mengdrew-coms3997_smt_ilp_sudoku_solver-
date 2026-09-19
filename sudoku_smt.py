"""
Sudoku solver via SMT (Z3).

Run:  pip install z3-solver
      python sudoku_smt.py
"""

from z3 import Int, Solver, And, Or, Distinct, sat

def solve(puzzle):
    """puzzle: 9x9 list of lists, 0 = blank. Returns solved grid or None."""
    X = [[Int(f"x_{r}_{c}") for c in range(9)] for r in range(9)]
    s = Solver()
    
    # overall, Z3 is just declaring variables and asserting conditions...

    # 1. every cell holds a digit 1..9
    s.add([And(1 <= X[r][c], X[r][c] <= 9) for r in range(9) for c in range(9)])

    # 2. each row has 9 distinct digits
    s.add([Distinct(X[r]) for r in range(9)])

    # 3. each column has 9 distinct digits
    s.add([Distinct([X[r][c] for r in range(9)]) for c in range(9)])

    # 4. each 3x3 box has 9 distinct digits
    s.add([Distinct([X[br + i][bc + j] for i in range(3) for j in range(3)])
           for br in (0, 3, 6) for bc in (0, 3, 6)])

    # 5. the given clues are fixed
    s.add([X[r][c] == puzzle[r][c]
           for r in range(9) for c in range(9) if puzzle[r][c] != 0])

    if s.check() != sat:
        return None
    m = s.model()
    return [[m[X[r][c]].as_long() for c in range(9)] for r in range(9)]


def count_solutions(puzzle, limit=2):
    """Uniqueness check: re-solve while forbidding each solution found."""
    X = [[Int(f"x_{r}_{c}") for c in range(9)] for r in range(9)]
    s = Solver()
    s.add([And(1 <= X[r][c], X[r][c] <= 9) for r in range(9) for c in range(9)])
    s.add([Distinct(X[r]) for r in range(9)])
    s.add([Distinct([X[r][c] for r in range(9)]) for c in range(9)])
    s.add([Distinct([X[br + i][bc + j] for i in range(3) for j in range(3)])
           for br in (0, 3, 6) for bc in (0, 3, 6)])
    s.add([X[r][c] == puzzle[r][c]
           for r in range(9) for c in range(9) if puzzle[r][c] != 0])

    n = 0
    while n < limit and s.check() == sat:
        m = s.model()
        n += 1
        # block this exact assignment, ask for another
        s.add(Or([X[r][c] != m[X[r][c]] for r in range(9) for c in range(9)]))
    return n


def show(g):
    for r in range(9):
        if r % 3 == 0:
            print("+-------+-------+-------+")
        print("| " + " | ".join(
            " ".join(str(g[r][c]) if g[r][c] else "." for c in range(b, b + 3))
            for b in (0, 3, 6)) + " |")
    print("+-------+-------+-------+")


def parse(s):
    """81-char string, '.' or '0' for blanks."""
    s = "".join(ch for ch in s if ch in "0123456789.")
    assert len(s) == 81, f"expected 81 cells, got {len(s)}"
    d = [0 if ch in ".0" else int(ch) for ch in s]
    return [d[i * 9:(i + 1) * 9] for i in range(9)]


PUZZLES = {
    # classic "hardest" puzzle (Arto Inkala style), 21 clues
    "hard": "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
    # a gentle one
    "easy": "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79",
    # no clues at all -- SMT happily invents a valid grid
    "empty": "." * 81,
}

if __name__ == "__main__":
    import sys, time
    name = sys.argv[1] if len(sys.argv) > 1 else "hard"
    grid = parse(PUZZLES.get(name, name))
    print(f"\n[{name}] puzzle:")
    show(grid)
    t = time.time()
    out = solve(grid)
    dt = time.time() - t
    if out is None:
        print("UNSAT -- no solution exists.")
    else:
        print(f"\nsolved in {dt*1000:.1f} ms:")
        show(out)
        n = count_solutions(grid)
        print("solution is unique" if n == 1 else f"at least {n} solutions")
