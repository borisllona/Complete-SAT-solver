#!/usr/bin/python
#######################################################################
# Copyright 2016 Josep Argelich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################
from __future__ import annotations
# Libraries

import sys
import os
import random
import signal
import time
from collections import OrderedDict

# Classes
from typing import Optional, List


class CNF():
    """A CNF formula """

    def __init__(self, cnf_file_name):
        """
        Initialization
        num_vars: Number of variables
        num_clauses: Number of clauses
        clause_length: Length of the clauses
        clauses: List of clauses
        """
        self.unique_sign: List[Optional[int]] = []
        self.num_vars = None
        self.num_clauses = None
        self.clauses = []
        self.dictionary = []
        self.unit_clauses = []
        self.read_cnf_file(cnf_file_name)
        self.pure_literal()

    def pure_literal(self):
        return filter(not None, self.unique_sign)

    def unit_propagation(self) -> Interpretation:
        inter_vars = [None] * (self.num_vars + 1)
        unit_lits = 0
        is_unit_lit = [False] * (self.num_vars + 1)
        while unit_lits != len(self.unit_clauses):
            unit_lits = 0
            for l in self.unit_clauses:
                unit_lits += 1
                if is_unit_lit[l]:
                    continue
                inter_vars[abs(l)] = 1 if l > 0 else 0
                self.remove_clauses(l)
                self.remove_literal(-l)
                is_unit_lit[l] = True
            self.unit_clauses = get_unrepeat_order(
                list(map(lambda x: x[0], filter(lambda x: len(x) == 1, self.clauses))))
        self.unit_clauses = list(map(lambda x: abs(x), self.unit_clauses))
        return Interpretation(self.num_vars, [None] * (self.num_vars + 1), self.unit_clauses)

    def remove_clauses(self, literal):
        for c in self.dictionary[literal]:
            self.clauses[c - 1] = [literal]

    def remove_literal(self, literal):
        clauses = self.dictionary[literal]
        for c in clauses:
            self.clauses[c - 1].remove(literal)

    def read_cnf_file(self, cnf_file_name):
        instance = open(cnf_file_name, "r")
        for l in instance:
            if l[0] == "c":
                continue
            if l[0] == "p":
                sl = l.split()
                self.num_vars = int(sl[2])
                self.num_clauses = int(sl[3])
                self.unique_sign = [[v + 1, 0] for v in range(self.num_vars)]
                self.dictionary = [[] for _ in range(self.num_vars * 2 + 1)]
                continue
            if l.strip() == "":
                continue
            sl = list(map(int, l.split()))
            sl.pop()
            if len(sl) == 0:
                sys.stdout.write('\ns UNSATISFIABLE\n')
                sys.exit()
            elif len(sl) == 1:
                self.unit_clauses.append(sl[0])
            self.get_sign(sl)
            self.clauses.append(sl)

    def get_sign(self, sl):
        for i in sl:
            self.dictionary[i].append(len(self.clauses) + 1)
            num_lit, found = self.unique_sign[abs(i) - 1]
            if found is None:
                continue
            if found == 0:
                if i > 0:
                    self.unique_sign[abs(i) - 1][1] += 1
                elif i < 0:
                    self.unique_sign[abs(i) - 1][1] -= 1
                continue
            if i > 0 > found or found > 0 > i:
                self.unique_sign[abs(i) - 1][1] = None

    def show(self):
        """Prints the formula to the stdout"""

        sys.stdout.write("c Random CNF formula\n")
        sys.stdout.write("p cnf %d %d\n" % (self.num_vars, self.num_clauses))
        for c in self.clauses:
            sys.stdout.write("%s 0\n" % " ".join(map(str, c)))

    @staticmethod
    def get_unrepeat_order(ls):
        return list(OrderedDict.fromkeys(ls))

    def __str__(self):
        return f'cnf:\n\tclauses: {self.clauses}\n\tunique_sign: {self.unique_sign}\n\tdict: {self.dictionary}\n\tunit: {self.unit_clauses}'


class Interpretation():
    """An interpretation is an assignment of the possible values to variables"""

    def __init__(self, num_vars, vars, cnf=None):
        """
        Initialization
        TODO
        """
        self.num_vars = num_vars
        self.vars = vars  # [None] * (self.num_vars + 1)
        self.cnf: Optional[CNF] = cnf

    def cost(self):
        cost = 0
        for c in self.cnf.clauses:
            length = len(c)
            for l in c:
                if self.vars[abs(l)] == None or (l < 0 and self.vars[abs(l)] == 0) or (
                        l > 0 and self.vars[abs(l)] == 1):  # Undef or Satisfies clause
                    break
                else:
                    length -= 1
            if length == 0:  # If all the literals al falsified, clause falsified
                cost += 1
        return cost

    def copy(self):
        new = Interpretation(self.num_vars)
        new.vars = list(self.vars)
        return new

    def show(self):
        if self.vars[self.num_vars] == None:
            sys.stdout.write('\ns UNSATISFIABLE\n')
        else:
            sys.stdout.write('\ns SATISFIABLE\nv ')
            for v, s in enumerate(self.vars[1:]):
                if not s:
                    sys.stdout.write('-')
                sys.stdout.write('%i ' % (v + 1))
            sys.stdout.write('0\n')

    def unit_propagation(self):
        pass


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr

    return start


class Solver():
    """The class Solver implements an algorithm to solve a given problem instance"""

    def __init__(self, cnf):
        """
        Initialization
        TODO
        """
        self.cnf: CNF = cnf
        self.best_sol = None
        self.best_cost = cnf.num_clauses + 1

    def get_last(self, order: List[int]):
        for i in range(1, order[0]):
            yield i
        for p in range(0, len(order) - 1):
            for i in range(order[p] + 1, order[p + 1]):
                yield i
        for i in range(order[-1] + 1, self.cnf.num_vars + 1):
            yield i

    def solve(self):
        """
        Implements an algorithm to solve the instance of a problem
        TODO:
        PureLiteralRule
        Selection of variable, check heuristics
        Not always asign variable to 0?
        Recursive?
        """
        curr_sol = self.cnf.unit_propagation()
<<<<<<< HEAD
        num_order = len(self.cnf.unit_clauses)  # None - 0 - 1
        order = self.cnf.unit_clauses # [1, 5, 7, 10] -> [2, 3, 4, 6, 8] [1,2,3,5]
        for i in range(0,len(order)-1):
            if order[i+1]-order[i] > 1: 
                print(order[i]+1)
        
=======
        curr_sol.cnf = self.cnf
        num_order = 1  # None - 0 - 1
        order = self.cnf.unit_clauses  # [1, 5, 7, 10] -> [2, 3, 4, 6, 8] [1,2,3,5]
        if order:
            order = [0] + order + list(self.get_last(order))
        else:
            order = list(range(self.cnf.num_vars))
        print(order)
        print(self.cnf.clauses)
        print(order)
>>>>>>> 28bae28fdb88eddd3164f3e36ce233cd443666c9
        while num_order > 0:
            var = order[num_order]
            if curr_sol.vars[var] == 1:  # Backtrack
                curr_sol.vars[var] = None
                num_order = num_order - 1
                continue
            if curr_sol.vars[var] == None:  # Extend left branch
                curr_sol.vars[var] = 0
            else:  # Extend right branch
                curr_sol.vars[var] = 1
            if curr_sol.cost() == 0:  # Undet or SAT
                if num_order == self.cnf.num_vars:  # SAT
                    return curr_sol
                else:  # Undet
                    num_order = num_order + 1
        return curr_sol

    # def unit_propagation():


# Main
def main():
    if len(sys.argv) < 1 or len(sys.argv) > 2:
        sys.exit("Use: %s <cnf_instance>" % sys.argv[0])

    if os.path.isfile(sys.argv[1]):
        cnf_file_name = os.path.abspath(sys.argv[1])
    else:
        sys.exit("ERROR: CNF instance not found (%s)." % sys.argv[1])

    # Read cnf instance
    cnf = CNF(cnf_file_name)
    print(cnf)
    # Create a solver instance with the problem to solve
    solver = Solver(cnf)
    # Solve the problem and get the best solution found
    best_sol = solver.solve()
    # Show the best solution found
    best_sol.show()


if __name__ == '__main__':
    # Check parameters
    main()
