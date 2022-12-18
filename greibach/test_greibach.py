import unittest

from greibach.Grammar import Grammar
from greibach.Greibach import Greibach


class TestGreibach(unittest.TestCase):

    def test_greibach_with_lambda(self):
        self.assertRaises(Exception, lambda: Greibach(Grammar({'E': ['ε'],})))

    def test_greibach_unified(self):
        self.assertRaises(Exception, lambda: Grammar(
            Greibach( {'E': ['TE', 'T'], 'T': ['FT', 'F'], 'F': ['(E)', 'a']}
            )))
