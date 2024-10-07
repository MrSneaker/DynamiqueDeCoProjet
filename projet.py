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

    def derive_conclusion(self, subset):
            conclusions = set()
            for arg in self.arguments:
                print(f'rule : {arg}')
                if arg.get_premises() is not None and arg.get_premises().issubset(subset):
                    conclusions.add(arg.get_conclusion())
            return conclusions if conclusions else None


        
    # def compute_normal_attacks(self):
    #     normal_attacks = set()
    #     assumptions_list = list(self.assumptions)

    #     all_subsets = [set(combo) for r in range(len(assumptions_list) + 1) for combo in itertools.combinations(assumptions_list, r)]
        
    #     def derive_conclusion(subset):
    #         conclusions = set()
    #         for arg in self.arguments:
    #             print(f'rule : {arg}')
    #             if arg.get_premises() is not None and arg.get_premises().issubset(subset):
    #                 conclusions.add(arg.get_conclusion())
    #         return conclusions if conclusions else None

    #     for X in all_subsets:
    #         for Y in all_subsets:

    #             claim_y = derive_conclusion(Y)
    #             if claim_y is None:
    #                 continue

    #             working_claims = set()
                
    #             in_pref = False
                
    #             for claim in claim_y:
    #                 for x_prime in X:
    #                     if self.check_preference(claim, x_prime):
    #                         in_pref = True
    #                         break
    #                 else:
    #                     if claim in [self.assumptions_and_contraries.get(x) for x in X]:
    #                         working_claims.add(claim)

    #             if working_claims:
    #                 if not any(self.check_preference(claim, x_prime) for claim in working_claims for x_prime in X):
    #                     X_str = ', '.join(map(str, X))
    #                     Y_str = ', '.join(map(str, Y))
    #                     normal_attacks.add(f"{X_str} -> {Y_str}")

    #     return normal_attacks
    
    def compute_normal_attacks2(self):
        normal_attacks = set()
        assumptions_list = list(self.assumptions)

        all_subsets = [set(combo) for r in range(len(assumptions_list) + 1) for combo in itertools.combinations(assumptions_list, r)]
        
        for X in all_subsets:
            for Y in all_subsets:
                
                claim_y = self.derive_conclusion(Y)
                claim_x = self.derive_conclusion(X)
                
                claim_x_none = False
                claim_y_none = False
                
                if claim_x is None:
                    claim_x_none = True
                
                if claim_y is None:
                    claim_y_none = True
                
                in_pref_y = False
                if not claim_y_none:
                    for claim in claim_y:
                        for x_prime in X:
                            if self.check_preference(claim, x_prime):
                                in_pref_y = True
                                break
                
                if not claim_x_none:
                    in_pref_x = False
                    for claim in claim_x:
                        for y_prime in Y:
                            if self.check_preference(claim, y_prime):
                                in_pref_x = True
                                break
                
                if not claim_y_none:
                    if not any(self.check_preference(claim, x_prime) for claim in claim_y for x_prime in X) and not in_pref_y:
                            X_str = ', '.join(map(str, X))
                            Y_str = ', '.join(map(str, Y))
                            normal_attacks.add(f"{X_str} -> {Y_str}")
                
                if not claim_x_none:
                    if not any(self.check_preference(claim, y_prime) for claim in claim_x for y_prime in Y) and not in_pref_x:
                            X_str = ', '.join(map(str, X))
                            Y_str = ', '.join(map(str, Y))
                            normal_attacks.add(f"{Y_str} -> {X_str}")
        return normal_attacks
                
    
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