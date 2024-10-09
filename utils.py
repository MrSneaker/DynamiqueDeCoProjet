import re
from projet import *

def parse_input(input_string: str):
    language = set()
    rules = set()
    assumptions_and_contraries = {}
    prefs = dict()
    lines = input_string.strip().split('\n')
    for line in lines:
        if line.startswith('L:'):
            L = re.findall(r'\w+', line[2:])
            for l in L:
                language.add(Literals(l, None))
        elif line.startswith('C('):
            key, value = line.split(': ')
            key = re.findall(r'\((.*?)\)', key)[0]
            value = value.strip()
            assumptions_and_contraries[Literals(key, None)] = Literals(value, None)
        elif line.startswith('[r'):
            match = re.match(r'\[r\d+\]:\s*(\w+)\s*<-\s*(.*)', line)
            if match:
                head = match.group(1)
                body = re.findall(r'\w+', match.group(2))
                set_premises = set()
                for p in body:
                    set_premises.add(Literals(p, None))
                rules.add(Rules(set_premises, Literals(head, None)))
        elif line.startswith('PREF:'):
            pref_match = re.findall(r'([\w\s,]+)\s*>\s*(\w+)', line.strip())

            for greater_group, lesser in pref_match:
                greater_elements = [elem.strip() for elem in greater_group.split(',')]
                for greater in greater_elements:
                    prefs[Literals(greater, None)] = Literals(lesser, None)
    return language, assumptions_and_contraries, rules, prefs

def load_and_read_file(file_path: str):
    with open(file_path, "r") as file:
        return parse_input(file.read())