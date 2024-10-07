from itertools import chain, product
import os

from cv2 import compare


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
    def __init__(self, premises: set[Literals], conclusion: Literals, rules_used: set[Rules]) -> None:
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

    def __str__(self) -> str:
        premises_str = ', '.join(
            map(str, self.premises)) if self.premises else "None"
        conclusion_str = str(self.conclusion)
        rules_str = ', '.join(map(str, self.rules_used)
                              ) if self.rules_used else "None"
        return f"Argument:\n  Premises: [{premises_str}]\n  Conclusion: {conclusion_str}\n  Rules used: [{rules_str}]"
    
    
class ABAPlus:
    def __init__(self, language: set[Literals], assumptions_and_contraries: dict[Literals: Literals], rules: set[Rules]) -> None:
        self.language = language
        self.assumptions = set([k for k,v in assumptions_and_contraries.items()])
        self.contraries = set([v for k,v in assumptions_and_contraries.items()])
        self.rules = rules
        
    def get_language(self):
        return self.language
    
    def get_assumptions(self):
        return self.assumptions
    
    def get_contraries(self):
        return self.contraries
    
    def get_rules(self):
        return self.rules
    
    def compute_arguments(self) -> set[Argument]:
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
        for rule in rules_used:
            print(f'rule used : {rule}')
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

        return computed_args
    
    def compute_attacks(self):
        return
    
    
    
if __name__ == "__main__":
    # exo 1 TD4
    langage = set[Literals]([Literals('a', None), Literals('b', None), Literals('c', None), Literals(
        'q', None), Literals('p', None), Literals('r', None), Literals('s', None), Literals('t', None)])
    
    assumptions = {Literals('a', None): Literals('r', None), Literals('b', None): Literals('s', None), Literals('c', None): Literals('t', None)}
    
    rules = set[Rules]([Rules(set([Literals('q', None), Literals('a', None)]), Literals('p', None)), Rules(set(), Literals('q', None)), Rules(set([Literals('b', None), Literals(
        'c', None)]), Literals('r', None)), Rules(set([Literals('p', None), Literals('c', None)]), Literals('t', None)), Rules(set([Literals('t', None)]), Literals('s', None))])

    aba = ABAPlus(langage, assumptions, rules)
    args = aba.compute_arguments()

    for arg in args:
        print(arg)

    print(f'number of args is {len(args)}')
