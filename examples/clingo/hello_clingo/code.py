"""
A first taste of clingo, the Answer Set Programming (ASP) solver from
the Potassco project.

ASP lets you describe a problem as a logic program: a set of facts and
rules. Clingo then finds "answer sets" -- assignments of atoms that
satisfy all the rules. It's particularly good at combinatorial puzzles,
scheduling, and configuration problems.

Docs: https://potassco.org/clingo/python-api/current/clingo/
"""
from IPython.core.display import display, HTML

import clingo
from clingo.control import Control
from clingo.symbol import Number, Function, String


heading("A tiny logic program: who likes what?")
note(
    "We declare three people and three foods, and a few facts about "
    "what each person likes. Clingo enumerates the model: the set of "
    "atoms that are true given our program."
)

# A logic program is just a string of ASP code. Lines ending with `.`
# are facts; `:-` introduces rules.
program = """
person(alice).
person(bob).
person(carol).

food(pizza).
food(salad).
food(sushi).

likes(alice, pizza).
likes(alice, sushi).
likes(bob, salad).
likes(carol, sushi).
likes(carol, pizza).

% A rule: two people are "food_friends" if they share a liked food.
food_friends(P1, P2) :- likes(P1, F), likes(P2, F), P1 != P2.
"""

# Control is the main entry point. We add the program, ground it
# (instantiate variables into concrete atoms), then solve.
control = Control()
control.add("base", [], program)
control.ground([("base", [])])

# `solve(on_model=...)` calls our callback for each answer set found.
answer_sets = []

def collect(model):
    # `model.symbols(shown=True)` gives the atoms in this answer set.
    # We capture them as strings for display.
    answer_sets.append([str(atom) for atom in model.symbols(atoms=True)])

control.solve(on_model=collect)

note(f"Clingo found <strong>{len(answer_sets)}</strong> answer set(s).")

# This program has a single answer set (no choices to make). Pull out
# just the food_friends atoms to show what the rule derived.
atoms = answer_sets[0]
friends = sorted(a for a in atoms if a.startswith("food_friends"))
note("Derived <code>food_friends</code> facts:")
display(HTML("<ul>" + "".join(f"<li><code>{f}</code></li>" for f in friends) + "</ul>"),
        append=True)
