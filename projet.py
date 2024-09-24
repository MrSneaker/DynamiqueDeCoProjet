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