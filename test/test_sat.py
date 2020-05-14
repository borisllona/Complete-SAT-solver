import unittest
from sat import sat


class MyTestCase(unittest.TestCase):


    def test_pure_literal(self):
        cnf = sat.CNF(cnf_file_name='cnfs_test/pure_literal.cnf')
        assert cnf.num_vars == 10
        assert cnf.num_clauses == 6
        for lit in (cnf.pure_literal()):
            assert lit[1] is not None


if __name__ == '__main__':
    unittest.main()
