#!/usr/bin/env python
import sys
from functools import lru_cache


def parse(filename):
    clauses = []
    unit_clauses = []
    for line in open(filename):
        if line[0] == 'p':
            variables = int(line.split()[2])
            continue
        if line[0] == 'c':
            continue
        clause = [int(x) for x in line[:-2].split()]
        if len(clause) == 1:
            unit_clauses.append(clause)
        clauses.append(clause)
    return variables, clauses, unit_clauses


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


def get_literal(formula, weight=2):
    counter = {}
    for clause in formula:
        for literal in clause:
            if abs(literal) in counter:
                counter[abs(literal)] += weight ** -len(clause)
            else:
                counter[abs(literal)] = weight ** -len(clause)
    return max(counter, key=counter.get)


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


def solve(formula, assignment, unit=None):
    formula, unit_assignment = unit_propagation(formula, unit)
    assignment += unit_assignment
    if formula == - 1:
        return []
    if formula == []:
        return assignment

    variable = get_literal(formula)
    solution = solve(bcp(formula, variable), assignment + [variable])
    if not solution:
        solution = solve(bcp(formula, -variable), assignment + [-variable])

    return solution


def jeroslow_wang_2_sided(formula):
    return get_literal(formula)


def get_weighted_counter(formula, weight=2):
    counter = {}
    occs = {}
    for clause in formula:
        for literal in clause:
            if literal in counter:
                counter[literal] += weight ** -len(clause)
                occs[literal] += 1
            else:
                counter[literal] = weight ** -len(clause)
                occs[literal] = 1
    return counter, occs


@lru_cache()
def w(occ, count):
    return occ * count


def solver_satz(formula):
    counter, occs = get_weighted_counter(formula)
    h = {}
    for i in counter.keys():
        h[i] = w(occs[i], counter[i]) * w(occs[-i], counter[-i]) * 2 ** 10 + w(occs[i], counter[i]) + w(occs[-i],
                                                                                                        counter[-i])
    return max(h, key=h.get)


def main():
    variables, clauses, unit = parse(sys.argv[1])

    solution = solve(clauses, [], unit)

    if solution:
        fill = lambda i: i if i not in solution and -i not in solution else None
        solution += list(filter(lambda x: x is not None, map(fill, range(1, variables + 1))))
        # solution += [i for i in range(1, variables + 1) if i not in solution and -i not in solution]
        solution.sort(key=abs)
        print('s SATISFIABLE' + '\n' + 'v ' + ' '.join([str(x) for x in solution]) + ' 0')
    else:
        print('s UNSATISFIABLE')


if __name__ == '__main__':
    main()
