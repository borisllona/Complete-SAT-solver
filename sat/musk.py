#!/usr/bin/env python
import sys


def parse(filename):
    clauses = []
    unit_clauses = []
    for line in open(filename):
        if line.startswith('c'):
            continue
        if line.startswith('p'):
            n_vars = line.split()[2]
            continue
        clause = [int(x) for x in line[:-2].split()]
        if len(clause) == 1:
            unit_clauses.append(clause[0])
        clauses.append(clause)
    return clauses, int(n_vars), unit_clauses


def bcp(formula, unit):
    modified = []
    for clause in formula:
        if unit in clause:
            continue
        if -unit in clause:
            new_clause = [x for x in clause if x != -unit]
            if not new_clause:
                return -1
            modified.append(new_clause)
        else:
            modified.append(clause)
    return modified


def get_weighted_abs_counter(formula, weight=2):
    counter = {}
    for clause in formula:
        for literal in clause:
            if abs(literal) in counter:
                counter[abs(literal)] += weight ** -len(clause)
            else:
                counter[abs(literal)] = weight ** -len(clause)
    return counter


def unit_propagation(formula, unit_clauses=None):
    assignment = []
    if unit_clauses is None:
        unit_clauses = [c for c in formula if len(c) == 1]
    while unit_clauses:
        unit = unit_clauses[0]
        formula = bcp(formula, unit[0])
        assignment += [unit[0]]
        if formula == -1 or not formula:
            return formula, assignment
        unit_clauses = [c for c in formula if len(c) == 1]
    return formula, assignment


def backtracking(formula, assignment, unit=None):
    formula, unit_assignment = unit_propagation(formula, unit)
    assignment = assignment + unit_assignment
    if formula == - 1:
        return []
    if not formula:
        return assignment

    variable = jeroslow_wang_2_sided(formula)
    solution = backtracking(bcp(formula, variable), assignment + [variable])
    if not solution:
        solution = backtracking(bcp(formula, -variable), assignment + [-variable])

    return solution


def jeroslow_wang_2_sided(formula):
    counter = get_weighted_abs_counter(formula)
    return max(counter, key=counter.get)


# Main

def main():
    clauses, n_vars, unit = parse(sys.argv[1])

    solution = backtracking(clauses, [], unit)

    if solution:
        solution += [x for x in range(1, n_vars + 1) if x not in solution and -x not in solution]
        solution.sort(key=abs)
        print('s SATISFIABLE')
        print('v ' + ' '.join([str(x) for x in solution]) + ' 0')
    else:
        print('s UNSATISFIABLE')


if __name__ == '__main__':
    main()
