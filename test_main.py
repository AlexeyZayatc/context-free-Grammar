from re import M
import unittest

from main import Grammar
from main import BOOL_MODE, GRAMMAR_MODE


class MyTestCase(unittest.TestCase):
    def test_grammar_axiom_not_in_non_terminals(self):
        self.assertRaises(Exception, lambda: Grammar(
            {'E', 'T', 'F'},
            {'a', '(', ')', '+', '*'},
            {
                'E': ['F'],
                'F': ['(E)', 'Ta']
            },
            'Q'
        ))

    def test_grammar_content_independency(self):
        self.assertRaises(Exception, lambda: Grammar(
            {'E', 'T', 'F', 'Z'},
            {'a', '(', ')', '+', '*'},
            {
                'E': ['F'],
                'F': ['(E)', 'Ta'],
                'Y': ['E']
            },
            'E'
        ))

    def test_grammar_remove_useless_symbols_should_stay_the_same(self):
        original_grammar: Grammar = Grammar(
            {'S'},
            {'1', '0'},
            {
                'S': ['0', '1', '0S', '1S']
            },
            'S'
        )

        grammar_without_useless_symbols = original_grammar.remove_useless_symbols()

        self.assertEqual(original_grammar,grammar_without_useless_symbols)

        test_case2: Grammar = Grammar(
            {'S','A','B'},
            {'a','b'},
            {'S': ['a','A'], 'A': ['AB'], 'B': 'b'},
            'S'
            )

        grammar_without_useless_symbols= test_case2.remove_useless_symbols()
        test_case2_answer: Grammar = Grammar(
            {'S'},
            {'a'},
            {'S': ['a']},
            'S'
            )

        self.assertEqual(grammar_without_useless_symbols,test_case2_answer)

    def test_grammar_remove_unreachable_symbols(self):
        test_case1: Grammar = Grammar(
            {'S'},
            {'1', '0'},
            {
                'S': ['0', '1', '0S', '1S']
            },
            'S'
        )

        attemp = test_case1.remove_unreachable_symbols()
        self.assertEqual(test_case1,attemp)

        test_case2: Grammar = Grammar(
            {'S','A','B','C'},
            {'1','2','3'},
            {
            'S': ['A'],
            'A': ['B'],
            'B': ['C'],
            },
            'S'
        )
        test_case2_answer: Grammar = Grammar(
            {'S','A','B','C'},
            set(),
            {
            'S': ['A'],
            'A': ['B'],
            'B': ['C'],
            },
            'S'
            )
        attemp=test_case2.remove_unreachable_symbols()
        self.assertEqual(test_case2_answer,attemp)

        test_case3: Grammar = Grammar(
            {'S','A','B','C'},
            {'a','b','c'},
            {
            'S': ['ab','a'],
            'A': ['B'],
            'B': ['C']
            },
            'S'
            )
        test_case3_answer: Grammar = Grammar(
            {'S'},
            {'a','b'},
            {
            'S': ['ab','a']
            },
            'S'
            )
        attemp = test_case3.remove_unreachable_symbols()
        self.assertEqual(test_case3_answer,attemp)

        test_case4: Grammar = Grammar(
            {'S','A','B','C'},
            {'a','b','c'},
            {
            'S': ['S'],
            'A': ['bBa'],
            'B': ['cCa'],
            'C': ['ccc']
            },
            'S'
            )
        test_case4_answer: Grammar = Grammar(
            {'S'},
            set(),
            {
            'S': ['S']
            },
            'S'
            )
        attemp = test_case4.remove_unreachable_symbols()
        self.assertEqual(test_case4_answer,attemp)

        test_case5: Grammar = Grammar(
            {'E','F','T'},
            {'+','*','(',')','a'},
            {
            'E': ['E+T','T'],
            'F': ['(E)', 'a']
            },
            'E'
            )
        test_case5_answer: Grammar = Grammar(
            {'E','T'},
            {'+'},
            {
            'E': ['E+T','T'],
            },
            'E'
            )
        attemp = test_case5.remove_unreachable_symbols()
        self.assertEqual(test_case5_answer,attemp)
        

        
    def test_grammar_is_not_empty_when_its_not_empty(self):
        empty_grammar: Grammar = Grammar(
            {'A', 'B'},
            {'0', '1'},
            {
                'A': ['B'],
                'B': ['1']
            },
            'A'
        )
        empty_grammar_terminal_chain_achieved: Grammar = Grammar(
            {'A','B','S','C','D'},  
            {'a','b','c','d'},
            {'S': ['aAa'], 'A': ['bBb'], 'B': ['cCc'], 'C': ['dDd'], 'D': ['abcd']},
            'S'
            )
        empty_grammar_terminal_chain_with_extra_routes: Grammar = Grammar(
            {'A','B','S','C','D', 'F'},
            {'a','b','c','d'},
            {'S': ['aAa'], 'A': ['bBb', 'Cdd'], 'B': ['cDc'], 'C': ['F'], 'D': ['abcd']},
            'S'
            )
        self.assertTrue(empty_grammar.is_not_empty(ret_flag=BOOL_MODE))
        self.assertTrue(empty_grammar_terminal_chain_achieved.is_not_empty(ret_flag=BOOL_MODE))
        self.assertTrue(empty_grammar_terminal_chain_with_extra_routes.is_not_empty(ret_flag=BOOL_MODE))

    def test_grammar_is_not_empty_when_its_empty(self):
        empty_grammar: Grammar = Grammar(
            {'A'},
            {'0'},
            {},
             'A'
            )
        empty_grammar_no_axiom_rule: Grammar = Grammar(
            {'A','B','S'},
            {'a,b,c'},
            {'A' : 'a', 'B': 'bcA'},
            'S'
            )
        empty_grammar_no_terminal_chain: Grammar = Grammar(
            {'A','B','S','C','D'},
            {'a','b','c','d'},
            {'S': ['aAa'], 'A': ['bBb'], 'B': ['cCc'], 'C': ['dDd']},
            'S'
            )
        empty_grammar_no_terminal_chain_recursion: Grammar = Grammar(
            {'A','B','S','C','D'},
            {'a','b','c','d'},
            {'S': ['aAa'], 'A': ['bBb'], 'B': ['cCc'], 'C': ['dAd']},
            'S'
            )
        empty_grammar_no_rule_to_good_symbol: Grammar = Grammar(
            {'A','B','C','S'},
            {'a','b','c'},
            {'S': ['AB'], 'C': ['aaa'], 'A':['BBB']},
            'S'
            )
        
        self.assertFalse(empty_grammar.is_not_empty(ret_flag=BOOL_MODE))
        self.assertFalse(empty_grammar_no_axiom_rule.is_not_empty(ret_flag=BOOL_MODE))
        self.assertFalse(empty_grammar_no_terminal_chain.is_not_empty(ret_flag=BOOL_MODE))
        self.assertFalse(empty_grammar_no_terminal_chain_recursion.is_not_empty(ret_flag=BOOL_MODE))
        self.assertFalse(empty_grammar_no_rule_to_good_symbol.is_not_empty(ret_flag=BOOL_MODE))

    def test_grammar_is_not_empty_grammar_output(self):
        test_case1: Grammar = Grammar(
            {'S', 'A', 'B', 'C', 'D', 'E', 'F', 'G'},
            {'a','b','c','d','e','f','g'},
            {
                'S': ['aAa','bbBbb','abcd'],
                'A': ['cCc', 'dDd'],
                'B': ['bDb', 'Eee'],
                'C': ['ccc','G'],
                'D': ['eeEee'],
                'E': ['gGg'],
                'G': ['G'],
                'F': ['fffAAA']
                },
            'S'
            )
        test_case1_answer: Grammar = Grammar(
            {'S', 'A', 'C', 'F'},
            {'a','b','c','d','e','f','g'},
            {
                'S': ['aAa','abcd'],
                'A': ['cCc'],
                'C': ['ccc'],
                'F': ['fffAAA']
                },
            'S'
            )
        test_case1=test_case1.is_not_empty(GRAMMAR_MODE)
        self.assertEqual(test_case1,test_case1_answer)
        
if __name__ == '__main__':
    unittest.main()
        
