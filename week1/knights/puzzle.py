from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


# Exclusive or function
def Xor(a, b):
    return Not(Biconditional(a, b))


# Puzzle 0
knowledge0 = And(
    # One must be a knight xor a Knave
    Xor(AKnight, AKnave),
    # A says "I am both a knight and a knave."
    Biconditional(AKnight, And(AKnight, AKnave)),
)

# Puzzle 1
knowledge1 = And(
    # One must be a knight xor a Knave
    Xor(AKnight, AKnave),
    Xor(BKnight, BKnave),
    # A says "We are both knaves."
    Biconditional(AKnight, And(AKnave, BKnave)),
    # B says nothing.
)

# Puzzle 2
knowledge2 = And(
    # One must be a knight xor a Knave
    Xor(AKnight, AKnave),
    Xor(BKnight, BKnave),
    # A says "We are the same kind."
    Biconditional(AKnight, Biconditional(AKnight, BKnight)),
    # B says "We are of different kinds."
    Biconditional(BKnight, Xor(AKnight, BKnight)),
)

# Puzzle 3
knowledge3 = And(
    # One must be a knight xor a Knave
    Xor(AKnight, AKnave),
    Xor(BKnight, BKnave),
    Xor(CKnight, CKnave),
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Xor(
        Biconditional(AKnight, AKnight),
        Biconditional(AKnight, AKnave),
    ),
    # B says "A said 'I am a knave'."
    Biconditional(BKnight, Biconditional(AKnight, AKnave)),
    # B says "C is a knave."
    Biconditional(BKnight, CKnave),
    # C says "A is a knight."
    Biconditional(CKnight, AKnight),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
