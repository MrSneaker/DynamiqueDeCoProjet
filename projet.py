from itertools import product
import os

class Literals:
    
    def __init__(self,nom,neg):
        self.name = nom
        self.neg = neg

    def __str__(self) -> str:
        if self.neg:
            return f"{self.name}"
        else:
            return f"!{self.name}"
        
    def oppose(self):
        return Literals(self.name,not(self.neg))
    
    def __eq__(self, other):
        if self.name == other.name and self.neg == other.neg:
            return True
        return False
    
    def __hash__(self):
      return hash((self.name, self.neg))
    
class Rules:

    num_regle = 0

    def __init__(self,s1,s2,b) -> None:
        self.name = Rules.setRef()
        self.premises = s1
        self.conclusion = s2

    def __str__(self) -> str:
        premises_str = ', '.join(map(str, self.premises))
        #conclusion_str = ', '.join(map(str, self.conclusion))
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
  

class ArgumentsFinder:
    
    def __init__(self, language: set[Literals], assumptions: set[Literals], rules: set[Rules]) -> None:
        self.language = language
        self.assumptions = assumptions
        self.rules = rules
    
    def compute_arguments() -> set[Argument]:
        computed_args = set()
        

