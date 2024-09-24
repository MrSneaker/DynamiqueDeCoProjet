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
        self.defeasible = b

    def __str__(self) -> str:
        premises_str = ', '.join(map(str, self.premises))
        #conclusion_str = ', '.join(map(str, self.conclusion))
        conclusion_str = self.conclusion
        if self.defeasible:
            return f"r{self.name} : [{premises_str}] => [{conclusion_str}]"
        return f"r{self.name} : [{premises_str}] -> [{conclusion_str}]"
    
    @classmethod
    def setRef(cls):
        cls.num_regle += 1
        return cls.num_regle
    
    def __eq__(self, other):
        if isinstance(other, Rules):
            return (
                self.premises == other.premises and 
                self.conclusion == other.conclusion and 
                self.defeasible == other.defeasible
            )
        return False
    
    def __hash__(self):
      return hash((self.conclusion, self.defeasible)) * hash(tuple(self.premises))