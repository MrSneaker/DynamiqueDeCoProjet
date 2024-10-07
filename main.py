from utils import parse_input
from projet import *

# exo 1 TD4
langage = set[Literals]([Literals('a', None), Literals('b', None), Literals('c', None), Literals(
    'q', None), Literals('p', None), Literals('r', None), Literals('s', None), Literals('t', None)])

assumptions = {Literals('a', None): Literals('r', None), Literals('b', None): Literals('s', None), Literals('c', None): Literals('t', None)}

rules = set[Rules]([Rules(set([Literals('q', None), Literals('a', None)]), Literals('p', None)), Rules(set(), Literals('q', None)), Rules(set([Literals('b', None), Literals(
    'c', None)]), Literals('r', None)), Rules(set([Literals('p', None), Literals('c', None)]), Literals('t', None)), Rules(set([Literals('t', None)]), Literals('s', None))])

aba = ABAPlus(langage, assumptions, rules)
args = aba.compute_arguments()
# for arg in args:
#     print(arg)
print(f'number of args is {len(args)}')

langage, assumptions, rules = parse_input("""L: [a,b,c,q,p,r,s,t]
A: [a,b,c]
C(a): r
C(b): s
C(c): t
[r1]: p <- q,a
[r2]: q <-
[r3]: r <- b,c
[r4]: t <- p,c
[r5]: s <- t
PREF: a > c
""")

aba2 = ABAPlus(langage, assumptions, rules)
args2 = aba2.compute_arguments()
# for arg2 in args2:
#     print(arg2)
print(f'number of args using parser is {len(args2)}')