import itertools
import re
from collections import defaultdict
from itertools import chain, product
import os

class Literals:

    def __init__(self, nom, neg):
        self.name = nom
        self.neg = neg

    def __str__(self) -> str:
        if not self.neg:
            return f"{self.name}"
        else:
            return f"!{self.name}"

    def oppose(self):
        return Literals(self.name, not (self.neg))

    def __eq__(self, other):
        if self.name == other.name and self.neg == other.neg:
            return True
        return False

    def __hash__(self):
        return hash((self.name, self.neg))


class Rules:

    num_regle = 0

    def __init__(self, s1, s2) -> None:
        self.name = Rules.setRef()
        self.premises = s1
        self.conclusion = s2

    def __str__(self) -> str:
        premises_str = ', '.join(map(str, self.premises))
        # conclusion_str = ', '.join(map(str, self.conclusion))
        conclusion_str = self.conclusion
        return f"r{self.name} : [{conclusion_str}] <- [{premises_str}]"

    @classmethod
    def setRef(cls):
        cls.num_regle += 1
        return cls.num_regle

    def __eq__(self, other):
        if isinstance(other, Rules):
            return (
                self.premises == other.premises and
                self.conclusion == other.conclusion
            )
        return False

    def __hash__(self):
        return hash((self.conclusion)) * hash(tuple(self.premises))


class Argument:
    
    _id_counter = 1
    
    def __init__(self, premises: set[Literals], conclusion: Literals, rules_used: set[Rules]) -> None:
        self.id = Argument._id_counter
        Argument._id_counter += 1
        self.premises = premises
        self.conclusion = conclusion
        self.rules_used = rules_used

    def get_premises(self) -> set[Literals] | None:
        if len(self.premises) == 0:
            return None
        else:
            return self.premises

    def get_conclusion(self) -> Literals:
        return self.conclusion

    def get_rules_used(self) -> set[Rules]:
        return self.rules_used
    
    def get_id(self):
        return self.id

    def __str__(self) -> str:
        premises_str = ', '.join(
            map(str, self.premises)) if self.premises else "None"
        conclusion_str = str(self.conclusion)
        rules_str = ', '.join(map(str, self.rules_used)
                              ) if self.rules_used else "None"
        return f"A{self.id}:  {conclusion_str} <- [{premises_str}]\n  Rules used: [{rules_str}]"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Argument):
            return False
        return (self.premises == other.premises and
                self.conclusion == other.conclusion and
                self.rules_used == other.rules_used)
    
    def __hash__(self) -> int:
        if self.rules_used is not None:
            return hash(self.id) * hash(self.conclusion) * hash(tuple(self.premises)) * hash(tuple(self.rules_used))
        else:
            return hash(self.id) * hash(self.conclusion) * hash(tuple(self.premises))
    
    
class ABAPlus:
    def __init__(self, language: set[Literals], assumptions_and_contraries: dict[Literals: Literals], rules: set[Rules], prefs: dict[Literals: Literals]) -> None:
        self.language = language
        self.assumptions = set([k for k,v in assumptions_and_contraries.items()])
        self.assumptions_and_contraries = assumptions_and_contraries
        self.rules = rules
        self.arguments = set[Argument]()
        self.prefs = prefs
        
    def get_language(self):
        return self.language
    
    def get_assumptions(self):
        return self.assumptions
    
    def get_contraries(self):
        return self.contraries
    
    def get_rules(self):
        return self.rules
    
    def compute_arguments(self) -> set[Argument]:
        if len(self.arguments) != 0:
            return self.arguments
        
        computed_args = set()
        rules_usable = self.rules

        rules_used = []
        for rule in rules_usable:
            rule_activable = len(
                self.assumptions.intersection(rule.premises)) >= len(rule.premises)
            if rule_activable or len(rule.premises) == 0:
                arg_premises = self.assumptions.intersection(rule.premises)
                new_arg = Argument(
                    premises=arg_premises, conclusion=rule.conclusion, rules_used=set([rule]))
                computed_args.add(new_arg)
                rules_used.append(rule)
        rules_usable.difference_update(rules_used)

        for assumption in self.assumptions:
            computed_args.add(Argument(set([assumption]), assumption, None))

        old_args = computed_args.copy()
        new_args = computed_args.copy()
        while True:
            rules_used = []
            for rule in rules_usable:
                used_args_conclusions = set(
                    [arg.get_conclusion() for arg in old_args]).intersection(rule.premises)
                rule_activable = len(used_args_conclusions) >= len(rule.premises)
                if rule_activable or len(rule.premises) == 0:
                    premises_used = set(
                        premise
                        for arg in old_args
                        if arg.get_conclusion() in used_args_conclusions and arg.get_premises() is not None
                        for premise in arg.get_premises()
                    )
                    arg_premises = self.assumptions.intersection(rule.premises)
                    full_premises = premises_used.union(arg_premises)
                    new_arg = Argument(
                        premises=full_premises, conclusion=rule.conclusion, rules_used=set([rule]))
                    if new_arg not in new_args:
                        new_args.add(new_arg)
                        rules_used.append(rule)
            
            rules_usable.difference_update(set(rules_used))
            if old_args == new_args:
                break
            else:
                old_args = new_args.copy()
        computed_args = new_args
        self.arguments = computed_args
        return self.arguments
    
    def compute_attacks(self):
        args = self.compute_arguments()
        attacks = set()
        
        for arg1 in args:
            for arg2 in args:                
                prems1 = arg1.get_premises()
                prems2 = arg2.get_premises()
                conclu1 = arg1.get_conclusion()
                conclu2 = arg2.get_conclusion()

                if prems1 is not None:
                    for prem in prems1:
                        if (prem, conclu2) in self.assumptions_and_contraries.items():
                            attacks.add("A" + str(arg2.get_id()) + " undermine " + "A" + str(arg1.get_id()))
                if prems2 is not None:
                    for prem in prems2:
                        if (prem, conclu1) in self.assumptions_and_contraries.items():
                            attacks.add("A" + str(arg1.get_id()) + " undermine " + "A" + str(arg2.get_id()))
        
        return attacks
    
        
    def check_preference(self, claim, x_prime):
        """Vérifie si la préférence entre deux éléments existe et retourne True si elle est valide."""
        return (claim, x_prime) in self.prefs.items()
    
    def check_preference_set(self, X: set, Y: set):
        score_x = 0
        score_y = 0
        
        X = set(X)
        Y = set(Y)
        # si X contient uniquement un élément préféré  et qu'il est différent de Y il est forcément préféré à Y
        if len(X) == 1 and X.issubset(self.prefs.keys()) and X != Y:
            return True
        
        for x in X:
            for y in Y:
                if self.check_preference(x, y) and x not in Y:
                    score_x += 1 / (len(X) * len(Y))
                if self.check_preference(y, x) and y not in X:
                    score_y += 1 / (len(X) * len(Y))
            
        
        return (score_x > score_y)
    
    def compute_normal_attacks(self):
        self.compute_arguments()
        attacks = set()
        all_subsets = []
        
        for r in range(1, len(self.assumptions) + 1):
            all_subsets.extend(itertools.combinations(self.assumptions, r))
        
        for X in all_subsets:
            for Y in all_subsets:
                
                X_str = ', '.join(str(x) for x in X)
                Y_str = ', '.join(str(y) for y in Y)
                                
                claims = set()
                for arg in self.arguments:
                    prems = arg.get_premises()
                    if prems is not None:
                        if prems.issubset(X):
                            claims.add(arg.get_conclusion())
                
                if not self.check_preference_set(Y, X):
                    if any(self.assumptions_and_contraries[y] == claim for y in Y for claim in claims):
                        X_str = ', '.join(str(x) for x in X)
                        Y_str = ', '.join(str(y) for y in Y)
                        attacks.add(f"{{{X_str}}} -> {{{Y_str}}}")
        return attacks

if __name__ == "__main__":
    # exo 1 TD4
    langage = set[Literals]([Literals('a', None), Literals('b', None), Literals('c', None), Literals(
        'q', None), Literals('p', None), Literals('r', None), Literals('s', None), Literals('t', None)])
    
    assumptions = {Literals('a', None): Literals('r', None), Literals('b', None): Literals('s', None), Literals('c', None): Literals('t', None)}
    
    rules = set[Rules]([Rules(set([Literals('q', None), Literals('a', None)]), Literals('p', None)), Rules(set(), Literals('q', None)), Rules(set([Literals('b', None), Literals(
        'c', None)]), Literals('r', None)), Rules(set([Literals('p', None), Literals('c', None)]), Literals('t', None)), Rules(set([Literals('t', None)]), Literals('s', None))])

    prefs = {Literals('a', None): Literals('b', None)}
    
    aba = ABAPlus(langage, assumptions, rules, prefs)
    args = aba.compute_arguments()
    
    for arg in args:
        print(arg)
        
    print(f'number of args is {len(args)}')
    
    attacks = aba.compute_attacks()
    for attack in attacks:
        print(attack)
    
    normal_attacks = aba.compute_normal_attacks()
    print(f'len normal att: {len(normal_attacks)}')
    
    for n_att in normal_attacks:
        print(n_att)