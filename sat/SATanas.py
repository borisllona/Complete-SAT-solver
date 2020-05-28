#!/usr/bin/env python
import sys
from collections import defaultdict
from functools import lru_cache


def parse(filename):
    clauses, unit_clauses = [], []
    for line in open(filename):
        if line[0] == 'p':
            variables = int(line.split()[2])
            continue
        if line[0] == 'c':
            continue
        clause = [int(x) for x in line[:-2].split()]
        clauses.append(clause)
    return variables, clauses


def new_formula(formula, unit):
    result = []
    for clause in formula:
        if unit in clause:
            continue
        if -unit in clause:
            new_clause = list(filter(lambda x: x != -unit, clause))
            if not new_clause:
                return 0
            result.append(new_clause)
        else:
            result.append(clause)
    return result


@lru_cache(maxsize=512)
def acc_weight(weight, len_clause):
    return weight ** -len_clause


def get_literal(formula, weight=3):
    counter = defaultdict(float)
    for clause in formula:
        for literal in clause:
            counter[abs(literal)] += acc_weight(weight, len(clause))
    return max(counter, key=counter.get)


def unit_propagation(formula, unit=None):
    assignment = []
    unit_clauses = [c for c in formula if len(c) == 1]
    while unit_clauses:
        unit = unit_clauses[0]
        formula = new_formula(formula, unit[0])
        assignment += [unit[0]]
        if formula == -1:
            return -1, []
        if not formula:
            return formula, assignment
        unit_clauses = [c for c in formula if len(c) == 1]
    return formula, assignment



def solve(formula, assignment, unit=None):
    formula, unit_assignment = unit_propagation(formula, unit)
    assignment = assignment + unit_assignment
    if formula == 0:
        return []
    if not formula:
        return assignment
    variable = get_literal(formula)
    print(variable)
    solution = solve(new_formula(formula, variable), assignment + [variable])
    if not solution:
        solution = solve(new_formula(formula, -variable), assignment + [-variable])

    return solution


def main():
    variables, clauses = parse(sys.argv[1])
    solution = solve(clauses, [])
    if solution:
        solution += [x for x in range(1, variables + 1) if x not in solution and -x not in solution]
        solution.sort(key=abs)
        print('s SATISFIABLE' + '\n' + 'v ' + ' '.join([str(x) for x in solution]) + ' 0')
    else:
        print('s UNSATISFIABLE')


if __name__ == '__main__':
    main()